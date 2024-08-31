from comfy_execution.graph_utils import GraphBuilder
from comfy_execution.graph import ExecutionBlocker
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


class XYGridAccumulator(FeedbackNode):

    @classmethod
    def IS_CHANGED(cls, images, xy_grid_control, unique_id):
        return images, xy_grid_control, unique_id

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "xy_grid_control": ("XY_GRID_CONTROL",),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)
    FUNCTION = "run"
    CATEGORY = "QQNodes/XYGrid"

    image_batch = torch.Tensor()

    def run(self, images, xy_grid_control, unique_id):
        count, reset, row_texts, column_texts, max_columns, font_size, grid_gap = xy_grid_control
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
        if len(image_list) < count:
            return {"result": (ExecutionBlocker(None),), "ui": {"images": ui_result}}
        else:
            graph = GraphBuilder()
            grid_annotation_node = graph.node(
                "GridAnnotation", row_texts=row_texts, column_texts=column_texts, font_size=font_size)
            images_grid_by_columns_node = graph.node(
                "ImagesGridByColumns", images=image_list, annotation=grid_annotation_node.out(0), max_columns=max_columns, gap=grid_gap)
            return {
                "result": (images_grid_by_columns_node.out(0),),
                "ui": {"images": ui_result},
                "expand": graph.finalize()
            }


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


class AnyListIterator:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "counter": ("INT", {"default": 0}),
                "list": ("LIST",),
            }
        }

    RETURN_TYPES = "AXIS_VALUE",
    FUNCTION = "run"
    CATEGORY = "QQNodes/List"

    def run(self, counter, list):
        return (list[counter % len(list)],)


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
    RETURN_NAMES = tuple("output_" + chr(i)
                         for i in range(ord('a'), ord('a') + 7))
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


class TextSplitter:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": ""}),
                "delimiter": ("STRING", {"default": ","}),
            }
        }

    RETURN_TYPES = ("LIST",)
    FUNCTION = "run"
    CATEGORY = "QQNodes/Text"

    def run(self, text, delimiter):
        return (text.split(delimiter),)


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
                "page_size": ("INT", {"default": 10}),
                "label_length": ("INT", {"default": 50}),
                "font_size": ("INT", {"default": 50}),
                "grid_gap": ("INT", {"default": 20}),
                "index": ("QQINDEX", {})
            }
        }

    RETURN_TYPES = ("AXIS_VALUE", "AXIS_VALUE", "XY_GRID_CONTROL")
    RETURN_NAMES = ("row_value", "column_value", "xy_grid_control")
    FUNCTION = "run"
    CATEGORY = "QQNodes/XYGrid"

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("NaN")

    def run(self, row_list, column_list, row_prefix, column_prefix, page_size, label_length, font_size, grid_gap, index):
        total_grid_images = len(row_list) * len(column_list)
        adjusted_index = index % total_grid_images

        row_index = adjusted_index // len(column_list) % len(row_list)
        page_index = row_index // page_size
        images_pr_page = page_size * len(column_list)
        row_annotation = ";".join([self.insert_newline_on_word_boundaries(self.format_prefix(row_prefix, self.get_label(
            x)), label_length) for x in row_list[page_index * page_size: (page_index + 1) * page_size]])
        column_annotation = ";".join([self.insert_newline_on_word_boundaries(
            self.format_prefix(column_prefix, self.get_label(y)), label_length) for y in column_list])
        xy_grid_control = (min(images_pr_page, total_grid_images - page_index * page_size), adjusted_index %
                           images_pr_page, row_annotation, column_annotation, len(column_list), font_size, grid_gap)
        return {"result": (
            row_list[row_index],
            column_list[adjusted_index % len(column_list)],
            xy_grid_control,
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

    def insert_newline_on_word_boundaries(self, input_string, length=50):
        # Initialize the result string and the current index
        result = ""
        current_index = 0

        while current_index < len(input_string):
            # If the remaining string is shorter than the length, add it to the result and break
            if current_index + length >= len(input_string):
                result += input_string[current_index:]
                break

            # Find the nearest space before the next cut-off point
            next_cutoff = current_index + length
            space_index = input_string.rfind(' ', current_index, next_cutoff)

            # If a space is found, and it's not just the first character (avoiding leading spaces)
            if space_index > current_index:
                # Add the substring up to the space and a newline
                result += input_string[current_index:space_index] + '\n'
                # Update the current index to the character after the space
                current_index = space_index + 1
            else:
                # If no suitable space is found, just cut at the specified length
                result += input_string[current_index:next_cutoff] + '\n'
                current_index = next_cutoff

        return result


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


class AnyToAny:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "any": (AnyType("*"),),
            }
        }

    RETURN_TYPES = (AnyType("*"),)
    FUNCTION = "run"
    CATEGORY = "QQNodes/Utils"

    def run(self, any):
        return (any,)


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


class AxisToAny(AxisBase):
    RETURN_TYPES = (AnyType("*"),)


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
    "Any List Iterator": AnyListIterator,
    "Load Lines From Text File": LoadLinesFromTextFile,
    "XY Grid Helper": XYGridHelper,
    "XY Grid Accumulator": XYGridAccumulator,
    "Slice List": SliceList,
    "Axis Pack": AxisPack,
    "Axis Unpack": AxisUnpack,
    "Text Splitter": TextSplitter,
    "Any To Any": AnyToAny,
    "Axis To Any": AxisToAny
}

load_axis_config_and_create_classes(NODE_CLASS_MAPPINGS, "axis-config.json")
load_axis_config_and_create_classes(
    NODE_CLASS_MAPPINGS, "custom-axis-config.json")
