# qq-nodes-comfyui
Custom nodes for comfyui

## XY Grid
Required custom mode packages
* https://github.com/WASasquatch/was-node-suite-comfyui
* https://github.com/LEv145/images-grid-comfy-plugin

### Workflow example
XY Grid over prompt and cfg value

![Image](https://github.com/kenjiqq/qq-nodes-comfyui/blob/main/workflows/xy-grid.png?raw=true)

Note the green primitive node should have control_after_generatation set to increment and when you want to start a grid generation set it's value to 0. It functions as a counter/ticker for the node to track what loop number we are on currently. Queue up prompts equal to the number of images required in the grid. The XY Grid helper node will show the total amount of images in the grid after the first Prompt is queued up so use that to know how many more Prompts to queue.