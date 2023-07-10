from comfy.model_management import InterruptProcessingException
import torch
import os
import hashlib
import folder_paths
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import torchvision.transforms as transforms


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


class TextListIndex(FeedbackNode):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "list": ("LIST",),
                "index": ("INT", {"default": 0}),
            },
        }

    RETURN_TYPES = "STRING",
    FUNCTION = "run"
    CATEGORY = "QQNodes/List"

    def run(self, list, index):
        return (list[index % len(list)],)


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


class NumberList:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "number_a": ("NUMBER", {"forceInput": True}),
            },
            "optional": {
                "number_b": ("NUMBER", {"forceInput": True}),
                "number_c": ("NUMBER", {"forceInput": True}),
                "number_d": ("NUMBER", {"forceInput": True}),
                "number_e": ("NUMBER", {"forceInput": True}),
                "number_f": ("NUMBER", {"forceInput": True}),
                "number_g": ("NUMBER", {"forceInput": True}),
            }
        }
    RETURN_TYPES = ("LIST",)
    FUNCTION = "run"

    CATEGORY = "QQNodes/List"

    def run(self, number_a, number_b=None, number_c=None, number_d=None, number_e=None, number_f=None, number_g=None):

        number_list = [number_a,]

        if number_b:
            number_list.append(number_b)
        if number_c:
            number_list.append(number_c)
        if number_d:
            number_list.append(number_d)
        if number_e:
            number_list.append(number_e)
        if number_f:
            number_list.append(number_f)
        if number_g:
            number_list.append(number_g)

        return (number_list,)


class NumberListIndex:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "list": ("LIST",),
                "index": ("INT", {"default": 0}),
            },
        }

    RETURN_TYPES = "NUMBER",
    FUNCTION = "run"
    CATEGORY = "QQNodes/List"

    def run(self, list, index):
        return (list[index % len(list)],)


class NumberListIterator:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "counter": ("INT", {"default": 0}),
                "list": ("LIST",),
                "repeats": ("INT", {"default": 1, "min": 1}),
            },
            "optional": {
            }
        }

    RETURN_TYPES = "NUMBER",
    FUNCTION = "run"
    CATEGORY = "QQNodes/List"

    def run(self, counter, list, repeats):
        return (list[counter // repeats % len(list)],)


class TextListIterator:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "counter": ("INT", {"default": 0}),
                "list": ("LIST",),
                "repeats": ("INT", {"default": 1, "min": 1}),
            }
        }

    RETURN_TYPES = "STRING",
    FUNCTION = "run"
    CATEGORY = "QQNodes/List"

    def run(self, counter, list, repeats):
        return (list[counter // repeats % len(list)],)


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


class XYGridHelper(FeedbackNode):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "row_list": ("LIST",),
                "column_list": ("LIST",),
                "index": ("INT", {"default": 0}),
            },
            "optional": {
                "row_prefix": ("STRING", {"default": ""}),
                "column_prefix": ("STRING", {"default": ""}),
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

    def run(self, row_list, column_list, index, row_prefix, column_prefix):
        if not self.validate_axis_types(row_list):
            raise Exception(
                "Invalid type for row_list: {}".format(type(row_list[0])))
        elif not self.validate_axis_types(column_list):
            raise Exception(
                "Invalid type for column_list: {}".format(type(column_list[0])))

        total_grid_images = len(row_list) * len(column_list)
        ui = self.get_feedback(
            f"Image {(index % total_grid_images) + 1} of {total_grid_images}")
        x_repeate = len(column_list)
        return dict({"result": (
            row_list[index // x_repeate % len(row_list)],
            column_list[index % len(column_list)],
            ";".join([self.truncate_string(self.format_prefix(row_prefix, str(x))) for x in row_list]),
            ";".join([self.truncate_string(self.format_prefix(column_prefix, str(y))) for y in column_list]),
            len(column_list),
            len(row_list) * len(column_list),
            index % total_grid_images
        )}, **ui)
    
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

    def validate_axis_types(self, list):
        for i in list:
            if not isinstance(i, (str, int, float)):
                return False
        return True


class AxisToString:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "axis": ("AXIS_VALUE", {}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "run"
    CATEGORY = "QQNodes/XYGrid"

    def run(self, axis):
        return (axis,)


class AxisToInt:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "axis": ("AXIS_VALUE",),
            }
        }

    RETURN_TYPES = ("INT",)
    FUNCTION = "run"
    CATEGORY = "QQNodes/XYGrid"

    def run(self, axis):
        return (axis,)

class AxisToFloat:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "axis": ("AXIS_VALUE",),
            }
        }

    RETURN_TYPES = ("FLOAT",)
    FUNCTION = "run"
    CATEGORY = "QQNodes/XYGrid"

    def run(self, axis):
        return (axis,)


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


NODE_CLASS_MAPPINGS = {
    "Number List": NumberList,
    "Text List Index": TextListIndex,
    "Number List Index": NumberListIndex,
    "Image Accumulator Start": ImageAccumulatorStart,
    "Image Accumulator End": ImageAccumulatorEnd,
    "Number List Iterator": NumberListIterator,
    "Text List Iterator": TextListIterator,
    "Load Lines From Text File": LoadLinesFromTextFile,
    "XY Grid Helper": XYGridHelper,
    "Axis To String": AxisToString,
    "Axis To Int": AxisToInt,
    "Axis To Float": AxisToFloat,
    "Slice List": SliceList,
}
