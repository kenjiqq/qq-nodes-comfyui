from comfy.model_management import InterruptProcessingException
from comfy.model_patcher import ModelPatcher
import torch
import os
import hashlib
import folder_paths
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import torchvision.transforms as transforms
import json

class AnyType(str):
    def __ne__(self, __value: object) -> bool:
        return False
    
class PackedAxisItem:
    def __init__(self, label, value):
        self.label = label
        self.value = value

class FeedbackNode:
    def __init__(self):
        self.output_dir = folder_paths.get_temp_directory()
        self.type = "temp"

    def get_feedback(self, text):
        image = self.create_text_image(text)
        return {"ui": {"images": self.preview_images([image])}}

    def preview_images(self, images, filename_prefix="QQNodes"):
        full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(
            filename_prefix, self.output_dir, images[0].shape[1], images[0].shape[0])
        results = list()
        for image in images:
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            file = f"{filename}_{counter:05}_.png"
            img.save(os.path.join(full_output_folder, file), compress_level=4)
            results.append({
                "filename": file,
                "subfolder": subfolder,
                "type": self.type
            })
            counter += 1
        return results

    def create_text_image(self, text, font_size=24, image_size=(256, 256), background_color=(255, 255, 255), text_color=(0, 0, 0), font_path=None):
        # Create a new image with the specified background color
        image = Image.new('RGB', image_size, background_color)

        # Create a font object with the specified size and font file
        font = font = ImageFont.truetype(
            str(Path(__file__).parent / "static" / "Roboto-Regular.ttf"), size=font_size)

        # Create a draw object
        draw = ImageDraw.Draw(image)

        # Calculate the text position at the center of the image
        text_width, text_height = draw.textsize(text, font=font)
        text_position = ((image_size[0] - text_width) //
                         2, (image_size[1] - text_height) // 2)

        # Draw the text on the image
        draw.text(text_position, text, font=font, fill=text_color)

        transform = transforms.ToTensor()
        image_tensor = transform(image)

        # reshape to shape expexted by preview_images
        image_tensor = image_tensor.permute(1, 2, 0)

        return image_tensor

class ImageAccumulatorStart(FeedbackNode):

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "count": ("INT", {"default": 1}),
            },
            "optional": {
                "reset": ("INT", {"default": 1}),
            }
        }

    RETURN_TYPES = ("IMAGE", "IMAGE_ACCUMULATOR_STATUS")
    RETURN_NAMES = ("images", "status")
    FUNCTION = "run"
    CATEGORY = "QQNodes/Image"

    image_batch = torch.Tensor()

    def run(self, images, count, reset):
        if reset == 0:
            self.image_batch = torch.Tensor()
        total_images = torch.cat((self.image_batch, images))
        processed_images = total_images[:count]
        remaining_images = total_images[count:]
        if len(remaining_images) > 0:
            self.image_batch = remaining_images
        else:
            self.image_batch = processed_images

        image_list = [processed_images[i]
                      for i in range(processed_images.shape[0])]
        ui_result = self.preview_images(image_list)
        return {"result": (image_list, len(image_list) >= count), "ui": {"images": ui_result}}


class ImageAccumulatorEnd(FeedbackNode):

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "status": ("IMAGE_ACCUMULATOR_STATUS",),
            },
        }

    RETURN_TYPES = "IMAGE",
    FUNCTION = "run"
    OUTPUT_NODE = True
    CATEGORY = "QQNodes/Image"

    def run(self, images, status):
        if not status:
            raise InterruptProcessingException()
        else:
            return (images,)


class AnyList:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_a": (AnyType("*"), {"forceInput": True}),
            },
            "optional": {
                "input_b": (AnyType("*"), {"forceInput": True}),
                "input_c": (AnyType("*"), {"forceInput": True}),
                "input_d": (AnyType("*"), {"forceInput": True}),
                "input_e": (AnyType("*"), {"forceInput": True}),
                "input_f": (AnyType("*"), {"forceInput": True}),
                "input_g": (AnyType("*"), {"forceInput": True}),
            }
        }
    RETURN_TYPES = ("LIST",)
    FUNCTION = "run"

    CATEGORY = "QQNodes/List"

    def run(self, input_a, input_b=None, input_c=None, input_d=None, input_e=None, input_f=None, input_g=None):

        input_list = [input_a,]

        if input_b:
            input_list.append(input_b)
        if input_c:
            input_list.append(input_c)
        if input_d:
            input_list.append(input_d)
        if input_e:
            input_list.append(input_e)
        if input_f:
            input_list.append(input_f)
        if input_g:
            input_list.append(input_g)

        return (input_list,)
    
class AxisPack: 
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_a": (AnyType("*"), {"forceInput": True}),
            },
            "optional": {
                "input_b": (AnyType("*"), {"forceInput": True}),
                "input_c": (AnyType("*"), {"forceInput": True}),
                "input_d": (AnyType("*"), {"forceInput": True}),
                "input_e": (AnyType("*"), {"forceInput": True}),
                "input_f": (AnyType("*"), {"forceInput": True}),
                "input_g": (AnyType("*"), {"forceInput": True}),
                "label": ("STRING", {"forceInput": False}),
            }
        }
    RETURN_TYPES = ("PACK",)
    FUNCTION = "run"

    CATEGORY = "QQNodes/XYGrid Axis"

    def run(self, input_a, input_b=None, input_c=None, input_d=None, input_e=None, input_f=None, input_g=None, label=""):

        input_list = [input_a,]

        if input_b:
            input_list.append(input_b)
        if input_c:
            input_list.append(input_c)
        if input_d:
            input_list.append(input_d)
        if input_e:
            input_list.append(input_e)
        if input_f:
            input_list.append(input_f)
        if input_g:
            input_list.append(input_g)
        
        return (PackedAxisItem(label, input_list),)
    
class AxisUnpack:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "axis": ("AXIS_VALUE",),
            },
        }
    RETURN_TYPES = tuple("AXIS_VALUE" for _ in range(7))
    RETURN_NAMES = tuple("output_" + chr(i) for i in range(ord('a'), ord('a') + 7))
    FUNCTION = "run"

    CATEGORY = "QQNodes/XYGrid Axis"

    def run(self, axis):
        padding = [None, ] * (7 - len(axis.value))
        return tuple(axis.value + padding)

class LoadLinesFromTextFile:
    @classmethod
    def INPUT_TYPES(s):
        input_dir = folder_paths.get_input_directory()
        files = [f for f in os.listdir(input_dir) if os.path.isfile(
            os.path.join(input_dir, f)) and f.endswith(".txt")]
        return {
            "required": {
                "file": [sorted(files), ],
            },
        }

    CATEGORY = "QQNodes/Text"

    RETURN_TYPES = ("LIST", )
    FUNCTION = "load"

    lines = []
    file_hash = None

    def load(self, file):
        file_path = folder_paths.get_annotated_filepath(file)
        if LoadLinesFromTextFile.getFileHash(file_path) != self.file_hash:
            with open(file_path, "r") as f:
                self.lines = f.readlines()
            self.file_hash = LoadLinesFromTextFile.getFileHash(file_path)

        return (self.lines,)

    @classmethod
    def getFileHash(cls, file_path):
        m = hashlib.sha256()
        with open(file_path, 'rb') as f:
            m.update(f.read())
        return m.digest().hex()

    @classmethod
    def VALIDATE_INPUTS(cls, file):
        if not folder_paths.exists_annotated_filepath(file):
            return "Invalid text file: {}".format(file)
        return True
    
    @classmethod
    def IS_CHANGED(cls, file):
        file_path = folder_paths.get_annotated_filepath(file)
        return cls.getFileHash(file_path)


class XYGridHelper():
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "row_list": ("LIST",),
                "column_list": ("LIST",),
            },
            "optional": {
                "row_prefix": ("STRING", {"default": ""}),
                "column_prefix": ("STRING", {"default": ""}),
                "index": ("QQINDEX", {} )
            }
        }

    RETURN_TYPES = ("AXIS_VALUE", "AXIS_VALUE", "STRING",
                    "STRING", "INT", "INT", "INT")
    RETURN_NAMES = ("row_value", "column_value", "row_annotation", "column_annotation",
                    "max_columns", "image_accumulator_count", "image_accumulator_reset")
    FUNCTION = "run"
    CATEGORY = "QQNodes/XYGrid"

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("NaN")

    def run(self, row_list, column_list, row_prefix, column_prefix, index):
        total_grid_images = len(row_list) * len(column_list)
        x_repeate = len(column_list)
        return {"result": (
            row_list[index // x_repeate % len(row_list)],
            column_list[index % len(column_list)],
            ";".join([self.truncate_string(self.format_prefix(row_prefix, self.get_label(x))) for x in row_list]),
            ";".join([self.truncate_string(self.format_prefix(column_prefix, self.get_label(y))) for y in column_list]),
            len(column_list),
            len(row_list) * len(column_list),
            index % total_grid_images
        ), "ui": {"total_images": [total_grid_images]}}
    
    def get_label(self, item):
        if isinstance(item, PackedAxisItem):
            return item.label
        else:
            return str(item)
        
    def format_prefix(self, prefix, text):
        if prefix:
            return f"{prefix}: {text}"
        else:
            return text

    def truncate_string(self, input_string, length=50):
        if len(input_string) > length:
            return input_string[:length - 3] + '...'
        else:
            return input_string

class SliceList:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "list": ("LIST",),
                "start": ("INT", {"default": 0}),
                "end": ("INT", {"default": 1}),
            }
        }

    RETURN_TYPES = ("LIST",)
    FUNCTION = "run"
    CATEGORY = "QQNodes/List"

    def run(self, list, start, end):
        return (list[start:end],)
    
class AxisBase:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "axis": ("AXIS_VALUE",),
            }
        }
    
    FUNCTION = "run"
    CATEGORY = "QQNodes/XYGrid Axis"

    def run(self, axis):
        return (axis,)

def create_axis_class(name):
    class_dict = {
        'RETURN_TYPES': (name,),
    }
    
    return type(f"AxisTo{name}", (AxisBase,), class_dict)

def load_axis_config_and_create_classes(node_map, config_file):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(dir_path, config_file)
    with open(config_path, 'r') as f:
        config = json.load(f)

    if not isinstance(config, list):
        raise ValueError("Axis config must be a json list")
    
    for axis_config in config:
        cls = create_axis_class(axis_config)
        globals()[axis_config] = cls
        node_map["Axis To " + axis_config] = cls


NODE_CLASS_MAPPINGS = {
    "Any List": AnyList,
    "Image Accumulator Start": ImageAccumulatorStart,
    "Image Accumulator End": ImageAccumulatorEnd,
    "Load Lines From Text File": LoadLinesFromTextFile,
    "XY Grid Helper": XYGridHelper,
    "Slice List": SliceList,
    "Axis Pack": AxisPack,
    "Axis Unpack": AxisUnpack
}

load_axis_config_and_create_classes(NODE_CLASS_MAPPINGS, "axis-config.json")
load_axis_config_and_create_classes(NODE_CLASS_MAPPINGS, "custom-axis-config.json")
