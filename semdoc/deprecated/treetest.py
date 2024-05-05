import urwid

# Example tree data structure
data = {"root": {"child1": {"grandchild1": {}}, "child2": {"test": {}, "test2": {}}}}


def menu(title, choices):
    body = [urwid.Text(title), urwid.Divider()]
    for c in choices:
        button = urwid.Button(c)
        urwid.connect_signal(button, "click", item_chosen, c)
        body.append(urwid.AttrMap(button, None, focus_map="reversed"))
    return urwid.ListBox(urwid.SimpleFocusListWalker(body))


def item_chosen(button, choice):
    response = urwid.Text(["You selected ", choice, "\n"])
    if choice in data:  # Navigate deeper if there are children
        choices = list(data[choice].keys())
        done = menu(f"Contents of {choice}", choices)
        main.original_widget = urwid.Filler(done)
    else:  # Leaf node action, customize as needed
        main.original_widget = urwid.Filler(response)


main = urwid.Padding(menu("Root", list(data["root"].keys())), left=2, right=2)
top = urwid.Overlay(
    main,
    urwid.SolidFill("\N{MEDIUM SHADE}"),
    align="center",
    width=("relative", 60),
    valign="middle",
    height=("relative", 60),
    min_width=20,
    min_height=9,
)
urwid.MainLoop(top, palette=[("reversed", "standout", "")]).run()
