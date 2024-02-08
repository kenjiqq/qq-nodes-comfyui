# qq-nodes-comfyui
Custom nodes for comfyui

## Install 
Clone repo into your custom_nodes folder in comfyui

## XY Grid
Required custom mode packages
* https://github.com/LEv145/images-grid-comfy-plugin
* https://github.com/WASasquatch/was-node-suite-comfyui ( for this specific workflow example, can be used without it)

### Workflow example
XY Grid over prompt and cfg value

![Image](https://github.com/kenjiqq/qq-nodes-comfyui/blob/main/workflows/xy-grid.png?raw=true)

Click the reset button in the XY Grid Helper node before starting a run to make a grid. Queue up prompts equal to the number of images required in the grid. The reset button in the XY Grid helper node will show the total amount of images in the grid after the first Prompt is queued up and what the current count is up to so queue up prompts until the counter and total are the same. For instance (4 of 4).

### Custom AxisTo converters

If you want to use other input/output types then the ones already supported by the library through the AxisToXXX converter nodes you can add the type you want to the custom-axis-config-json file locally and it will automatically generate a AxisTo converter node for this type.

### Nodes

#### XY Grid Helper

![Image](https://github.com/kenjiqq/qq-nodes-comfyui/blob/main/assets/xy-grid-helper.png?raw=true)

The node takes in a LIST for the row values and column values each and will iterate through each combination of them. To be able to use the row and column value output since the type of them are unknown one of the "Axis To X" nodes has to be used to convert to the correct type that can be connected to whatever other node you want to send the values to. 

"row_annotation", "column_annotation" and "max_columns" all connect up to the grid nodes from https://github.com/LEv145/images-grid-comfy-plugin

"image_accumulator_count" and "imag_accumulator_reset" connects to to the image accumulator node

Click the reset button before starting a new run to make a XY grid, as you queue up prompts it will show how many images need to be queued to finish the grid

#### Image Accumulator

![Image](https://github.com/kenjiqq/qq-nodes-comfyui/blob/main/assets/image-accumulator.png?raw=true)

Image Accumulator Start and Image Accumulator End must always be used together so the node is able to stop the execution of the downstream connected nodes until the grid is finished.

As images are generated the node will show a preview of all images generated so far so you can inspect them.

#### Grid nodes 

Refer to https://github.com/LEv145/images-grid-comfy-plugin for more information

#### Any List

![Image](https://github.com/kenjiqq/qq-nodes-comfyui/blob/main/assets/any-list.png?raw=true)

Convert any type into a LIST of that type

#### Load Lines From Text File

![Image](https://github.com/kenjiqq/qq-nodes-comfyui/blob/main/assets/load-lines-from-file.png?raw=true)

Utility node to make it easier to load prompts etc directly from a text file into a LIST for use with the XY Grid Helper. Put text file in your comfyui input/ folder
