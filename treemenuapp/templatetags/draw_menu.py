from typing import Iterable
from django import template
from treemenuapp.models import MenuNode

register = template.Library()

class MenuNodeInternal:
    """
    Internal class to manipulate menu nodes without any requests to the database.
    Used to decide which of the nodes will be visible.
    """
    def __init__(self, id, name, url, parent, children, priority, is_active, is_visibile):
        self.id = id
        self.name = name
        self.url = url
        self.children = children
        self.parent = parent
        self.priority = priority
        self.is_active = is_active
        self.is_visible = is_visibile
    @staticmethod
    def create_empty(node):
        return MenuNodeInternal(
            node.id,
            node.name,
            node.get_url(),
            parent=None,
            children=[],
            priority=node.priority,
            is_active=False,
            is_visibile=False,
        )
    
    def __repr__(self) -> str:
        s = self.name + " " + str([child.id for child in self.children])
        if self.is_visible:
            s += " (visible)"
        return s

def __find_active_node(
        node_dict: dict[str, MenuNodeInternal],
        current_path: str) -> MenuNodeInternal:
    """
    Find and return the active node in the node dictionary for the given current path.
    
    :param node_dict: Dictionary containing nodes
    :param current_path: Current path to search for
    :return: The active node if found, otherwise None
    """
    for n in node_dict.values():
        if n.url == current_path:
            n.is_active = True
            return n
    return None

def __fill_children(node_dict: dict[str, MenuNodeInternal], nodes: Iterable[MenuNode]) -> MenuNodeInternal:
    """
    Fill the children in the given node dictionary using data from the provided nodes and return the root node.

    :param node_dict: Dictionary containing nodes (to be modified)
    :param nodes: Django model objects for the menu nodes
    :return: Root node
    """
    root = None
    # Iterating through the Django nodes
    for n in nodes:
        if n.parent:
            # Setting the corresponding parent and children inside the node_dict
            node_dict[n.id].parent = node_dict[n.parent.id]
            node_dict[n.parent.id].children.append(node_dict[n.id])
        else:
            # Found root node
            root = node_dict[n.id]
    return root

def __calculate_visible(
        node_dict: dict[str, MenuNodeInternal],
        current_node: MenuNodeInternal) -> None:
    """
    Calculate the visibilities of the nodes.
    All the children of the active node and every its ancestor will be visible.

    :param node_dict: The node dictionary (to be modified)
    :param current_node: Currently open menu item
    """
    while current_node is not None:
        current_node.is_visible = True
        for child in current_node.children:
            child.is_visible = True
        current_node = current_node.parent

def __generate(
        nodes: Iterable[MenuNode],
        current_path: str) -> MenuNodeInternal:
    """
    Generate the MenuNodeInternal structure based on the Django model objects.
    Decides the active node based on the current_path.
    Returns the root node.
    """
    node_dict = {n.id: MenuNodeInternal.create_empty(n) for n in nodes}
    
    
    current_node = __find_active_node(node_dict, current_path)
    root = __fill_children(node_dict, nodes)

    if current_node is None:
        current_node = root
    __calculate_visible(node_dict, current_node)
    
    # Sorting the children and removing the ones that are not visible
    for k, v in node_dict.items():
        v.children = list(filter(lambda x: x.is_visible, v.children))
        v.children.sort(key=lambda x: x.priority)

    return root

@register.inclusion_tag("templatetags/menu.html", takes_context=True)
def draw_menu(context, menu_name):
    request = context.get("request")
    current_path = request.path
    # Select all the menu nodes for the given menu, together with their parents.
    # Uses a single query.
    #
    # Technically it is possible to do filtering for visible nodes here, but that would require either
    # really fragile (and probably unreadable) Django ORM code or a raw SQL query.
    # Since the number of menu nodes is unlikely to be >100, fetching more nodes than necessary is not an issue,
    # as long as it is done in a single query (like here).
    menu = MenuNode.objects.filter(menu__slug=menu_name).select_related('parent').all()
    # Generate the internal data structure for the visible nodes.
    # This does not perform any database queries.
    root_node = __generate(menu, current_path)
    return {
        'root_node': root_node
    }

@register.inclusion_tag("templatetags/menu_node.html", takes_context=True)
def draw_menu_node(context, node):
    return {
        'node': node
    }