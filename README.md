# qq-nodes-comfyui
Custom nodes for comfyui

## Install 
Clone repo into your custom_nodes folder in comfyui

## XY Grid
Required custom mode packages
* https://github.com/LEv145/images-grid-comfy-plugin ( used behind the scene through node expansion )
* https://github.com/WASasquatch/was-node-suite-comfyui ( for this specific workflow example, can be used without it )

### Workflow example
XY Grid over prompt and cfg value

![Image](https://github.com/kenjiqq/qq-nodes-comfyui/blob/main/workflows/xy-grid.png?raw=true)

## Usage instructions
Click the reset button in the XY Grid Helper node before starting a run to make a grid. Queue up prompts equal to the number of images required in the grid. The reset button in the XY Grid helper node will show the total amount of images in the grid after the first Prompt is queued up and what the current count is up to so queue up prompts until the counter and total are the same. For instance (4 of 4).

### Additional workflow examples

[Sampler Grid](workflows/sampler-grid.png) Using combo widgets in the grid, like sampler_name

[Axis Packing Grid](workflows/axis-packing-grid.png) Using axis packing to pass multiple items into an axis, in this case a unet, clip and vae


### Custom AxisTo converters

If you want to use other input/output types then the ones already supported by the library through the AxisToXXX converter nodes you can add the type you want to the custom-axis-config-json file locally and it will automatically generate a AxisTo converter node for this type.

### Nodes

#### XY Grid Helper

![Image](https://github.com/kenjiqq/qq-nodes-comfyui/blob/main/assets/xy-grid-helper.png?raw=true)

The node takes in a LIST for the row values and column values each and will iterate through each combination of them. To be able to use the row and column value output since the type of them are unknown one of the "Axis To X" nodes has to be used to convert to the correct type that can be connected to whatever other node you want to send the values to. 

"row_prefix, "column_prefix" you can set text that will be added before related label in the grid

"page_size" sets how many rows to generate before outputting the grid image, grids can become very large with high resolution images so can be a good idea to split them into smaller grids using this

"label_length" sets the max character length before the label will be broken into multiple lines

"font_size" font size for the labels of the grid axis

"grid_gap" size of the gap between images in the grid

Click the reset button before starting a new run to make a XY grid, as you queue up prompts it will show how many images need to be queued to finish the grid

#### XY Grid Accumulator

![Image](https://github.com/kenjiqq/qq-nodes-comfyui/blob/main/assets/xy-grid-accumulator.png?raw=true)

Accumulates images for the grid and stop the execution of the downstream connected nodes until the grid is finished.

Uses node expansion to inject the images-grid-comfy-plugin nodes behind the scene to generate the grid.

As images are generated the node will show a preview of all images generated so far so you can inspect them.

#### Grid nodes 

Refer to https://github.com/LEv145/images-grid-comfy-plugin for more information

#### Any List

![Image](https://github.com/kenjiqq/qq-nodes-comfyui/blob/main/assets/any-list.png?raw=true)

Convert any type into a LIST of that type

#### Text Splitter

![Image](https://github.com/kenjiqq/qq-nodes-comfyui/blob/main/assets/text-splitter.png?raw=true)

Simple node that just takes a string and splits it on some delimiter into a LIST that can be passed into a row/col. Use Axis to String on the output side and then convert the string to whatever type you need using for instance WAS nodes.

#### Load Lines From Text File

![Image](https://github.com/kenjiqq/qq-nodes-comfyui/blob/main/assets/load-lines-from-file.png?raw=true)

Utility node to make it easier to load prompts etc directly from a text file into a LIST for use with the XY Grid Helper. Put text file in your comfyui input/ folder

#### Axis Packing

![Image](https://github.com/kenjiqq/qq-nodes-comfyui/blob/main/assets/axis-packing.png?raw=true)

If you want to change multiple things in a row or column you can use the Axis Pack node to pack all the values you want to use and send that into the AnyList. On the output side of the XYGridHelper you then use Axis Unpack node to split the row/column into its components again.

Axis Pack node also allows you to set the label that will be used in the final grid image. So you can also use the node with just 1 input if you want to control the label

#### Any to Any

![Image](https://github.com/kenjiqq/qq-nodes-comfyui/blob/main/assets/any-to-any.png?raw=true)

WARNING: this is very hacky and disables all type checking in comfy so if you send in anything wrong you will not get any warnings and behaviour might be pretty random depening on what node you connect to.

This node should be able to take in any value (does not work with primitive node or reroute nodes) and connect to any other node regardless of if the types are compatible or not.
