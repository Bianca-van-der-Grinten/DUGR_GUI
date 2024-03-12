"""
Functions to handle common image formats for DUGR calculation

Currently available:
    - TechnoTeam Image formats: *.pus, *.pf, *.pcf
    - Ascii image: A textfile containing the pixel information
"""
import numpy as np
import re
from os.path import exists


def convert_tt_image_to_numpy_array(image_file: str):
    """
    Function that converts an image from the TechnoTeam image format to a numpy array

    Args:
        image_file: image file in one of the TechnoTeam image formats (*.pus, *.pf, *.pcf)

    Returns:
         image_array: Numpy array containing the pixel information
         header dict: Dictionary with all the image information stored in the TechnoTeam image headers
    """

    if not exists(image_file):
        print("\nThe entered image file does not exist!")
        return np.empty((0, 0)), {}

    if image_file[-3:] != 'pus' and image_file[-2:] != 'pf' and image_file[-3:] != 'pcf':
        print("The entered image file is not part of the TechnoTeam image file format!\nValid formats are:\n\t*.pus"
              "\n\t*.pf\n\t*.pcf")
        return np.empty((0, 0)), {}

    with open(image_file, "rb") as imageInput:
        data = imageInput.read()

    r = data.find(b'\x00')  # Finding 0 byte which separates header and pixel data

    header = data[:r].decode('utf-8')  # utf-8 decode header to text
    header_fmt = header.replace('\r', '')  # header formatting to pack key/value pair to dict
    header_fmt = header_fmt.replace('|', '')
    while header_fmt[-1] == '\n':  # Remove line breaks at the end of the header for header to dict conversion
        header_fmt = header_fmt[:-1]
    header_dict = dict(entry.split('=') for entry in header_fmt.split('\n'))  # Pack dict

    pixel_data = data[r + 1:]

    image_array = np.empty((0, 0))
    try:
        #  Camera Image
        if header_dict['Typ'] == 'Pic98::TPlane<unsigned short>':
            image_array = np.frombuffer(pixel_data, dtype='<H').reshape(int(header_dict['Lines']),
                                                                        int(header_dict['Columns']))

        #  Luminance Image
        elif header_dict['Typ'] == "Pic98::TPlane<float>":
            image_array = np.frombuffer(pixel_data, dtype=np.float32).reshape(int(header_dict['Lines']),
                                                                              int(header_dict['Columns']))

        # Color Image
        elif header_dict['Typ'] == "Pic98::TPlane<Pic98::TRGBFloatPixel>":
            image_array = np.frombuffer(pixel_data, dtype=np.float32).reshape((int(header_dict['Lines']),
                                                                               int(header_dict['Columns']), 3))
    except KeyError:
        print("The file type is one of the expected TechnoTeam formats (*.pus, *.pf. *.pcf)"
              "\nBut the header seems to be corrupted"
              "\nThe image type is not defined in the header")
        image_array = np.empty((0, 0))
        return image_array, header_dict

    return image_array, header_dict


def convert_ascii_image_to_numpy_array(image_file: str):
    """
    Function that converts an image from ascii format to a numpy array

    Args:
        image_file: Path to the image in the ascii format (*.txt). Each new line represents a new image row.

    Returns:
        image_array: Numpy array containing the pixel information
    """

    if image_file[-3:] != 'txt':
        print("The entered image file has to be of type *.txt")
        return np.empty((0, 0)), {}

    with open(image_file, 'r') as file_object:
        pixel_values = file_object.read().replace(',', '.').split('\n')[2:-1]

    image_array = np.genfromtxt(pixel_values, dtype=np.float32, delimiter='\t')
    return image_array
