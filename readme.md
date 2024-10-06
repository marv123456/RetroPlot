# Retro Plot

A python script to extract data from plots.

## Table of Contents

- [Description](#description)
- [Getting Started](#getting-started)
- [Author](#author)
- [Version history](#version-history)
- [Contributing](#contributing)
- [License](#license)


## Description

This python script generates a graphical interface to extract data from graphs using calibration curves and linear regressions. It helps users to perform reverse engineering to extrapolate the closest value from the graphed data. This tool is particularly useful for researchers and engineers who need to retrieve data represented only in graphs and not textually.

## Getting Started

### Dependencies

- **Python>=3.8**
- tk>=0.1.0
- pillow>=10.4.0
- numpy>=1.24.4
- scipy>=1.10.1
- scikit-learn>=1.3.2

### Installing

- Download from [here](https://github.com/marv123456/RetroPlot/blob/main/main.py?raw=True)
- Install requirements:

```
pip install -r requirements.txt
```


### Executing program

* To run the script execute:

```
python main.py
```

### Usage

Open an image using File>Open menu.

Right click on the image to add an X, Y value or the origin with values ​​(0,0). After adding two values, you can calculate the value of any point on the graph. When the cursor is over the image you can also adjust the selected pixel by moving the arrow keys.

You can crop the image to fix the view in the plot, just click over image and move the cursor.

![Crop image](https://github.com/marv123456/RetroPlot/blob/main/img/sample0.02.png?raw=True)


## Author

- **Miguel Angel Ramos-Valdovinos** - [marv123456](https://github.com/marv123456)


## Version History

* 0.01
    * Prototype.
    * Linear regression.
    * Zoom of image.
    * Use keys to adjust the selected point.
* 0.02
    * Crop/Restore image

## Contributing
Contributions are welcome! Please submit a pull request or open an issue if you have suggestions or improvements.

## License

This project is licensed under the Apache 2.0 License - see the LICENSE file for details
