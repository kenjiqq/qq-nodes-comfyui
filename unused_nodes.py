
# class NumberListIndex:
#     @classmethod
#     def INPUT_TYPES(cls):
#         return {
#             "required": {
#                 "list": ("LIST",),
#                 "index": ("INT", {"default": 0}),
#             },
#         }

#     RETURN_TYPES = "NUMBER",
#     FUNCTION = "run"
#     CATEGORY = "QQNodes/List"

#     def run(self, list, index):
#         return (list[index % len(list)],)


# class NumberListIterator:
#     @classmethod
#     def INPUT_TYPES(cls):
#         return {
#             "required": {
#                 "counter": ("INT", {"default": 0}),
#                 "list": ("LIST",),
#                 "repeats": ("INT", {"default": 1, "min": 1}),
#             },
#             "optional": {
#             }
#         }

#     RETURN_TYPES = "NUMBER",
#     FUNCTION = "run"
#     CATEGORY = "QQNodes/List"

#     def run(self, counter, list, repeats):
#         return (list[counter // repeats % len(list)],)


# class TextListIterator:
#     @classmethod
#     def INPUT_TYPES(cls):
#         return {
#             "required": {
#                 "counter": ("INT", {"default": 0}),
#                 "list": ("LIST",),
#                 "repeats": ("INT", {"default": 1, "min": 1}),
#             }
#         }

#     RETURN_TYPES = "STRING",
#     FUNCTION = "run"
#     CATEGORY = "QQNodes/List"

#     def run(self, counter, list, repeats):
#         return (list[counter // repeats % len(list)],)

# class TextListIndex(FeedbackNode):
#     @classmethod
#     def INPUT_TYPES(cls):
#         return {
#             "required": {
#                 "list": ("LIST",),
#                 "index": ("INT", {"default": 0}),
#             },
#         }

#     RETURN_TYPES = "STRING",
#     FUNCTION = "run"
#     CATEGORY = "QQNodes/List"

#     def run(self, list, index):
#         return (list[index % len(list)],)