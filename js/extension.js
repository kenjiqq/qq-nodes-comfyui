import { app } from "../../../../scripts/app.js";

// Safe clone function to handle Proxy objects
function safeClone(obj) {
	try {
		return structuredClone(obj);
	} catch (error) {
		// Fallback to JSON method if structuredClone fails
		return JSON.parse(JSON.stringify(obj));
	}
}

app.registerExtension({
	name: "qq-nodes-comfyui",
	async beforeRegisterNodeDef(nodeType, nodeData, app) {
		if (nodeType?.comfyClass === "XY Grid Helper") {
			const onExecuted = nodeType.prototype.onExecuted;
			nodeType.prototype.onExecuted = function (message) {
				onExecuted?.apply(this, arguments);
				if (message?.total_images !== undefined) {
					const widget = this.widgets?.find((w) => w.qqId === "reset_button");
					if (widget !== undefined) {
						widget.qqTotalImages = message.total_images[0];
						widget.name = `Reset - ${widget.value} of ${widget.qqTotalImages}`;
					}
				}
			};
		}
	},
	getCustomWidgets(app) {
		return {
			QQINDEX(node, inputName, inputData, app) {
				const widget = node.addWidget("button", "Reset", 0, () => {
					widget.value = 0;
					widget.name = `Reset`;
				});
				widget.afterQueued = () => {
					widget.value += 1;
					widget.name = `Reset - ${widget.value} of ${widget.qqTotalImages}`;
				};
				widget.qqId = "reset_button";
				widget.qqInputName = inputName;
				return widget;
			}
		}
	},
	async setup(app) {
		/*
		 *     Highjack the graphToPrompt function to change the name of the reset button to what the python node expects
		 */
		const _original_graphToPrompt = app.graphToPrompt;
		app.graphToPrompt = async function () {
			const p = safeClone(await _original_graphToPrompt.apply(app)); // <-- replaced here
			for (const node of app.graph.findNodesByType("XY Grid Helper")) {
				const widget = node.widgets?.find((w) => w.qqId === "reset_button");
				const promptNode = p.output[node.id]
				if (widget !== undefined && promptNode !== undefined) {
					promptNode.inputs[widget.qqInputName] = promptNode.inputs[widget.name]
					delete promptNode.inputs[widget.name]
				}
			}
			return p;
		}
	}
});
