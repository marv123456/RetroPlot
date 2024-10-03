import tkinter as tk
from tkinter import Menu, filedialog, PanedWindow, ttk
from PIL import Image, ImageTk, ImageDraw
import numpy as np
from scipy import stats
from sklearn.linear_model import LinearRegression


# Reset all tables
def reset():
    global mx, bx, my, by
    mx = bx = my = by = None
    xtable.delete(*xtable.get_children())
    ytable.delete(*ytable.get_children())
    point_table.delete(*point_table.get_children())

# Click over treeview
def on_right_click(event, treeview):
    # Get the row under the cursor when right-clicked
    row_id = treeview.identify_row(event.y)
    if row_id:  # Check if a valid item was clicked
        global focused_table
        focused_table = treeview
        treeview.selection_set(row_id)  # Select the clicked row
        show_context_table(event)
    else:
        treeview.selection_remove(treeview.selection())  # Deselect any selection

def create_table(parent, cols):
    columns = ['Col' + str(count) for count in range(len(cols))]
    table = ttk.Treeview(parent, columns=columns, show='headings', height=4)
    for i in range(len(cols)):
        table.heading(columns[i], text=cols[i][0])
        table.column(columns[i], width=cols[i][1])
    table.pack(pady=5)
    return table


# Set # in table
def update_table(table):
    count = 0
    for item in table.get_children():
        count += 1
        values = list(table.item(item, 'values'))
        values[0] = count
        table.item(item, values=values)

def set_value_in_cell(row_index, column_index, new_value):
    items = xtable.get_children()  # Get all row IDs
    if row_index < len(items):
        item_id = items[row_index]  # Get the ID of the specified row
        current_values = list(xtable.item(item_id, 'values'))  # Get current values
        current_values[column_index] = new_value  # Update the specified column with the new value
        xtable.item(item_id, values=current_values)  # Set the updated values back to the row

def calculate_points():
    global mx, bx, my, by
    
    for item in point_table.get_children():
            values = list(point_table.item(item, 'values'))
            values[2] = float(values[1])*mx + bx if (mx and bx) else ''
            point_table.item(item, values=values)

    for item in point_table.get_children():
        values = list(point_table.item(item, 'values'))
        values[4] = float(values[3])*my + by if (my and by) else ''
        point_table.item(item, values=values)
        

def append_table_xy(table, pixel, value):
    table.insert('', 'end', values=('', pixel, value))
    update_table(table)
    

def append_table_point(table, pixelX, pixelY):
    table.insert('', 'end', values=('', pixelX, "", pixelY, ""))
    update_table(table)
    calculate_points()

#radio_var.get()

def get_regress(table, linear):
    list_x = []
    list_values = []
    for item in table.get_children():
        values = list(table.item(item, 'values'))
        list_x.append(float(values[1]))
        list_values.append(float(values[2]))
    x = np.array(list_x)
    y = np.array(list_values)
    if linear:
        m, b, r_value, p_value, std_err = stats.linregress(x, y)
        print('Mx: ' + str(m) + ' Bx: ' + str(b))
        return m, b
    else:
        x = x.reshape(-1, 1)
        log_y = np.log(y)
        model = LinearRegression()
        model.fit(x, log_y)
        return model

def calibrate_x():
    lineal = (x_radio_var.get() == 'Lineal')
    global mx, bx
    if len(xtable.get_children()) < 2:
        mx = None
        bx = None
        return
    mx, bx = get_regress(xtable, lineal)
    calculate_points()
    
def calibrate_y():
    lineal = (y_radio_var.get() == 'Lineal')
    global my, by
    if len(ytable.get_children()) < 2:
        my = None
        by = None
        return
    my, by = get_regress(ytable, lineal)
    calculate_points()

# Function to open and display a selected picture
def open_image():
    size = 400
    global img, img_tk, loaded_image
    file_path = filedialog.askopenfilename(
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
    )
    if file_path:
        loaded_image = Image.open(file_path)
        m = max(loaded_image.width, loaded_image.height)
        ratio = 1
        if m > size:
            ratio = size/m
        img = loaded_image.resize((int(loaded_image.width*ratio), int(loaded_image.height*ratio)))
        #img = loaded_image
        img_tk = ImageTk.PhotoImage(img)
        img_label.config(image=img_tk)
        img_label.image = img_tk

def update_zoom(orig_x, orig_y):
    if 0 <= orig_x < loaded_image.width and 0 <= orig_y < loaded_image.height:
        global menu_mouse_x, menu_mouse_y
        menu_mouse_x, menu_mouse_y = orig_x, orig_y
        pixel_value = loaded_image.getpixel((orig_x, orig_y))
        pixel_label.config(text=f"Pixel at ({orig_x}, {orig_y}): {pixel_value}")
        zoom_size = 50
        box_left = orig_x - zoom_size
        box_top = orig_y - zoom_size
        box_right = orig_x + zoom_size
        box_bottom = orig_y + zoom_size
        cropped_image = loaded_image.crop((box_left, box_top, box_right, box_bottom))
        zoomed_image = cropped_image.resize((200, 200))
        draw = ImageDraw.Draw(zoomed_image)
        center_x = zoomed_image.width // 2
        center_y = zoomed_image.height // 2
        point_radius = 1
        draw.ellipse((center_x - point_radius, center_y - point_radius,
                        center_x + point_radius, center_y + point_radius),
                        fill='red')
        zoomed_tk = ImageTk.PhotoImage(zoomed_image)
        zoom_label.config(image=zoomed_tk)
        zoom_label.image = zoomed_tk
        
def on_mouse_move(event):
    if loaded_image:
        orig_x = int(event.x * loaded_image.width / img.width)
        orig_y = int(event.y * loaded_image.height / img.height)
        update_zoom(orig_x, orig_y)
        
            


def show_context_table(event):
    global menu_mouse_x, menu_mouse_y
    menu_mouse_x, menu_mouse_y = event.x, event.y
    if len(focused_table['columns']) == 5:
        table_context_menu.entryconfig(1, state="disabled")
    elif len(focused_table['columns']) == 3:
        table_context_menu.entryconfig(1, state="normal")

    table_context_menu.tk_popup(event.x_root, event.y_root)
    

def show_context_menu(event):
    #global menu_mouse_x, menu_mouse_y
    #menu_mouse_x, menu_mouse_y = event.x, event.y
    context_menu.tk_popup(event.x_root, event.y_root)


def update_all():
    calibrate_x()
    calibrate_y()
    calculate_points()


def delete_selected_item():
    table = focused_table
    selected_item = table.selection()  # Get selected item
    if selected_item:
        table.delete(selected_item)  # Delete the selected item
    update_all()

def add_origin():
    global menu_mouse_x, menu_mouse_y
    append_table_xy(xtable, menu_mouse_x, 0)
    append_table_xy(ytable, menu_mouse_y, 0)

def add_x_value():
    global menu_mouse_x
    def on_yes(event=None):
        value = value_entry.get()  
        append_table_xy(xtable, menu_mouse_x, value)
        calibrate_x()
        dialog.destroy()

    def on_cancel(event=None):
        dialog.destroy()

    dialog = tk.Toplevel(root)
    dialog.title("Add X Value")
    dialog.geometry("300x150")

    dialog.bind("<Escape>", on_cancel)

    dialog.bind("<Return>", on_yes)

    label = tk.Label(dialog, text="Value:")
    label.pack(pady=10)

    value_entry = tk.Entry(dialog)
    value_entry.pack(pady=10)
    value_entry.focus_set()

    button_frame = tk.Frame(dialog)
    button_frame.pack(pady=10)

    cancel_button = tk.Button(button_frame, text="Cancel", command=on_cancel)
    cancel_button.pack(side=tk.LEFT, padx=5)
    
    yes_button = tk.Button(button_frame, text="Yes", command=on_yes)
    yes_button.pack(side=tk.LEFT, padx=5)
        

def add_y_value():
    global menu_mouse_y
    def on_yes(event=None):
        value = value_entry.get()
        append_table_xy(ytable, menu_mouse_y, value)
        calibrate_y()
        dialog.destroy()

    def on_cancel(event=None):
        dialog.destroy()

    dialog = tk.Toplevel(root)
    dialog.title("Add Y Value")
    dialog.geometry("300x150")

    dialog.bind("<Escape>", on_cancel)

    dialog.bind("<Return>", on_yes)

    label = tk.Label(dialog, text="Value:")
    label.pack(pady=10)

    value_entry = tk.Entry(dialog)
    value_entry.pack(pady=10)
    value_entry.focus_set()

    button_frame = tk.Frame(dialog)
    button_frame.pack(pady=10)

    cancel_button = tk.Button(button_frame, text="Cancel", command=on_cancel)
    cancel_button.pack(side=tk.LEFT, padx=5)
    
    yes_button = tk.Button(button_frame, text="Yes", command=on_yes)
    yes_button.pack(side=tk.LEFT, padx=5)

def add_point():
    global menu_mouse_x, menu_mouse_y
    append_table_point(point_table, menu_mouse_x, menu_mouse_y)
    calculate_points()
    

# Create the main window
root = tk.Tk()
root.title("RetroPlot")
root.geometry("800x600")

# Create a vertical paned window (split in two parts)
paned_window = PanedWindow(root, orient=tk.HORIZONTAL)
paned_window.pack(fill=tk.BOTH, expand=1)
# tools_frame = tk.Frame(paned_window, bg="lightgrey", width=30)
# paned_window.add(tools_frame)

# reset_button = tk.Button(
#     tools_frame, text="B", command=reset
# )
# reset_button.pack(pady=10)


data_frame = tk.Frame(paned_window, bg="lightgrey", width=200)
paned_window.add(data_frame)
image_frame = tk.Frame(paned_window, bg="white", width=600)
paned_window.add(image_frame)

# Menu bar
menu_bar = Menu(root)
file_menu = Menu(menu_bar, tearoff=0)
#file_menu.add_command(label="New")
file_menu.add_command(label="Open", command=open_image)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)
menu_bar.add_cascade(label="File", menu=file_menu)
root.config(menu=menu_bar)

# Function to be called when arrow keys are pressed
def on_arrow_key(event):
    if event.keysym == 'Up':
        update_zoom(menu_mouse_x, menu_mouse_y - 1 )
    elif event.keysym == 'Down':
        update_zoom(menu_mouse_x, menu_mouse_y + 1 )
    elif event.keysym == 'Left':
        update_zoom(menu_mouse_x - 1, menu_mouse_y)
    elif event.keysym == 'Right':
        update_zoom(menu_mouse_x + 1, menu_mouse_y)


# Bind arrow key events to the label only when mouse is over it
def bind_keys(event):
    root.bind("<Up>", on_arrow_key)
    root.bind("<Down>", on_arrow_key)
    root.bind("<Left>", on_arrow_key)
    root.bind("<Right>", on_arrow_key)

# Unbind the keys when the mouse leaves the label
def unbind_keys(event):
    root.unbind("<Up>")
    root.unbind("<Down>")
    root.unbind("<Left>")
    root.unbind("<Right>")


# Label where image is showed
img_label = tk.Label(image_frame)
img_label.pack(pady=20)  # Position the label in the right pane
img_label.bind('<Motion>', on_mouse_move)
img_label.bind("<Enter>", bind_keys)
img_label.bind("<Leave>", unbind_keys)
img_label.bind('<Button-3>', show_context_menu)

# Label where value of coursor is showed
pixel_label = tk.Label(image_frame, text="Pixel at (X, Y): Value", font=("Arial", 12))
pixel_label.pack()


# Label where the zoomed image is showed
zoom_label = tk.Label(image_frame)
zoom_label.pack(pady=10)


reset_button = tk.Button(
    data_frame, text="Reset", command=reset
)
reset_button.pack(pady=10)


label = tk.Label(data_frame, text="X-values", font=("Arial", 12), bg="lightgrey")
label.pack(pady=5)

# Create a frame to hold the radio buttons above the tables
x_radio_frame = tk.Frame(data_frame, bg="lightgrey")
x_radio_frame.pack(pady=5)

# Define a variable to hold the selected value (lineal or exponential)
x_radio_var = tk.StringVar(value="Lineal")

# Create the "Lineal" radio button
x_lineal_radio = tk.Radiobutton(
    x_radio_frame, text="Lineal", variable=x_radio_var, value="Lineal", bg="lightgrey", command=update_all
)
#x_lineal_radio.pack(side=tk.LEFT, padx=5)

# Create the "Exponential" radio button
x_exponential_radio = tk.Radiobutton(
    x_radio_frame, text="Exponential", variable=x_radio_var, value="Exponential", bg="lightgrey", command=update_all
)
#x_exponential_radio.pack(side=tk.LEFT, padx=5)


xtable = create_table(data_frame, [['#', 30],['Pixel', 60],['Value', 60]])
xtable.bind('<Button-3>', lambda event: on_right_click(event, xtable))

label = tk.Label(data_frame, text="Y-values", font=("Arial", 12), bg="lightgrey")
label.pack(pady=5)

# Create a frame to hold the radio buttons above the tables
y_radio_frame = tk.Frame(data_frame, bg="lightgrey")
y_radio_frame.pack(pady=5)

# Define a variable to hold the selected value (lineal or exponential)
y_radio_var = tk.StringVar(value="Lineal")

# Create the "Lineal" radio button
y_lineal_radio = tk.Radiobutton(
    y_radio_frame, text="Lineal", variable=y_radio_var, value="Lineal", bg="lightgrey", command=update_all
)
#y_lineal_radio.pack(side=tk.LEFT, padx=5)

# Create the "Exponential" radio button
y_exponential_radio = tk.Radiobutton(
    y_radio_frame, text="Exponential", variable=y_radio_var, value="Exponential", bg="lightgrey", command=update_all
)
#y_exponential_radio.pack(side=tk.LEFT, padx=5)



ytable = create_table(data_frame, [['#', 30],['Pixel', 60],['Value', 60]])
ytable.bind('<Button-3>', lambda event: on_right_click(event, ytable))


label = tk.Label(data_frame, text="Points", font=("Arial", 12), bg="lightgrey")
label.pack(pady=5)

point_table = create_table(data_frame, [['#', 30],['Pixel X', 60],['Value X', 60],['Pixel Y', 60],['Value Y', 60]])
point_table.bind('<Button-3>', lambda event: on_right_click(event, point_table))

def plot_table():
    table = focused_table
    if len(table['columns']) == 3:
        print('Si es')

# Menu over tables
table_context_menu = Menu(root, tearoff=0)
table_context_menu.add_command(label="Delete", command= lambda: delete_selected_item())
table_context_menu.add_command(label="Plot", command= lambda: plot_table())


# Menu over image
context_menu = Menu(root, tearoff=0)
context_menu.add_command(label="Add x value", command=add_x_value)
context_menu.add_command(label="Add y value", command=add_y_value)
context_menu.add_command(label="Add point", command=add_point)
context_menu.add_command(label="Add Origin", command=add_origin)

loaded_image = None
img = None
menu_mouse_x = 0
menu_mouse_y = 0
mx = None
my = None
bx = None
by = None

focused_table = None

root.mainloop()