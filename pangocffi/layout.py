from . import pango, gobject, ffi
from . import Context, FontDescription
from . import Alignment, Rectangle
import ctypes
from typing import Tuple, Optional


class Layout(object):
    """
    A Pango ``Layout`` represents an entire paragraph of text. It is
    initialized with a Pango :class:`Context`, UTF-8 string and set of
    attributes for that string. Once that is done, the set of formatted lines
    can be extracted from the object, the layout can be rendered, and
    conversion between logical character positions within the layout's text,
    and the physical position of the resulting glyphs can be made.
    """

    def __init__(self, context: Context):
        """
        Create a new ``Layout`` object with attributes initialized to default
        values for a particular :class:`Context`.

        :param context:
            the Pango :class:`Context`
        """
        self._init_pointer(pango.pango_layout_new(context.get_pointer()))

    def _init_pointer(self, pointer: ctypes.c_void_p):
        self._pointer = ffi.gc(pointer, gobject.g_object_unref)

    @classmethod
    def from_pointer(cls, pointer: ctypes.c_void_p) -> 'Layout':
        """
        Instantiates a ``Layout`` from a pointer.

        :return:
            the layout.
        """
        if pointer == ffi.NULL:
            raise ValueError('Null pointer')
        self = object.__new__(cls)
        cls._init_pointer(self, pointer)
        return self

    def get_pointer(self) -> ctypes.c_void_p:
        """
        Returns the pointer to this layout.

        :return:
            a pointer to the layout.
        """
        return self._pointer

    def get_context(self) -> Context:
        """
        Returns the Pango Context used for this layout.

        :return:
            the :class:`Context` for the layout.
        """
        return Context.from_pointer(
            pango.pango_layout_get_context(self._pointer)
        )

    def set_text(self, text: str) -> None:
        """
        Sets the text of the layout.

        Note that if you have used ``set_markup()`` or
        ``set_markup_with_accel()`` on the layout before, you may want to call
        ``set_attributes()`` to clear the attributes set on the layout from
        the markup as this function does not clear attributes.

        :param text:
            a valid UTF-8 string
        """
        text_pointer = ffi.new('char[]', text.encode('utf8'))
        pango.pango_layout_set_text(self._pointer, text_pointer, -1)

    def set_markup(self, markup: str) -> None:
        """
        Same as set_markup_with_accel(), but the markup text isn't scanned for
        accelerators.

        :param markup:
            marked-up text
        """
        markup_pointer = ffi.new('char[]', markup.encode('utf8'))
        pango.pango_layout_set_markup(self._pointer, markup_pointer, -1)

    def set_font_description(self, desc: Optional[FontDescription]) -> None:
        """
        Sets the default font description for the layout. If no font
        description is set on the layout, the font description from the
        layout's context is used.

        :param desc:
            the new ``FontDescription``, or ``None`` to unset the current
            ``FontDescription``.
        """
        if desc is None:
            pango.pango_layout_set_font_description(self._pointer, ffi.NULL)
        else:
            pango.pango_layout_set_font_description(
                self._pointer,
                desc.get_pointer()
            )

    def get_font_description(self) -> Optional[FontDescription]:
        """
        Returns the font description for the layout, if any.

        :return:
            the layout's ``FontDescription``, or ``None`` if the
            ``FontDescription`` from the layout's :class:`Context` is inherited.
        """
        desc_pointer = pango.pango_layout_get_font_description(self._pointer)
        if desc_pointer == ffi.NULL:
            return None
        return FontDescription.from_pointer(desc_pointer)

    def set_width(self, width: int) -> None:
        """
        Sets the width to which the lines of the layout should wrap or
        ellipsized. The default value is -1: no width set.

        :param width:
            the desired width in Pango units, or -1 to indicate that no
            wrapping or ellipsization should be performed.
        """
        pango.pango_layout_set_width(self._pointer, width)

    def get_width(self) -> int:
        """
        Returns the width to which the lines of the layout should wrap.

        :return:
             the width in Pango units, or -1 if no width set.
        """
        return pango.pango_layout_get_width(self._pointer)

    def set_height(self, height: int) -> None:
        """
        Sets the ``height`` to which the layout should be ellipsized at.
        There are two different behaviors, based on whether height is positive
        or negative.

        If ``height`` is positive, it will be the maximum height of the layout.
        Only lines would be shown that would fit, and if there is any text
        omitted, an ellipsis added. At least one line is included in each
        paragraph regardless of how small the height value is.
        A value of zero will render exactly one line for the entire layout.

        If height is negative, it will be the (negative of) maximum number of
        lines per paragraph. That is, the total number of lines shown may well
        be more than this value if the layout contains multiple paragraphs of
        text. The default value of -1 means that first line of each paragraph
        is ellipsized. This behavior may be changed in the future to act per
        layout instead of per paragraph. File a bug against pango at
        http://bugzilla.gnome.org/ if your code relies on this behavior.

        Height setting only has effect if a positive width is set on layout and
        ellipsization mode of layout is not ``Ellipsize.NONE``. The behavior
        is undefined if a height other than -1 is set and ellipsization mode
        is set to ``Ellipsize.NONE``, and may change in the future.

        :param height:
            the desired height of the layout in Pango units if positive, or
            desired number of lines if negative.
        """
        pango.pango_layout_set_height(self._pointer, height)

    def get_height(self) -> int:
        """
        Returns the height of the layout used for ellipsization.

        :return:
            the height, in Pango units if positive, or number of lines if
            negative.
        """
        return pango.pango_layout_get_height(self._pointer)

    def set_alignment(self, alignment: Alignment) -> None:
        """
        Sets the alignment for the layout: how partial lines are positioned
        within the horizontal space available.

        :param alignment:
            the alignment.
        """
        pango.pango_layout_set_alignment(self._pointer, alignment.value)

    def get_alignment(self) -> Alignment:
        """
        Returns the alignment for the layout: how partial lines are positioned
        within the horizontal space available.

        :return:
            the alignment.
        """
        return Alignment(pango.pango_layout_get_alignment(self._pointer))

    def get_extents(self) -> Tuple[Rectangle, Rectangle]:
        """
        Computes the logical and ink extents of the layout.
        Logical extents are usually what you want for positioning things.
        Note that both extents may have non-zero x and y.
        You may want to use those to offset where you render the layout.
        Not doing that is a very typical bug that shows up as right-to-left
        layouts not being correctly positioned in a layout with a set width.

        The extents are given in layout coordinates and in Pango units;
        layout coordinates begin at the top left corner of the layout.

        :return:
            a tuple containing two ``Rectangle`` objects.
            The first is the extent of the layout as drawn.
            The second is the logical extent of the layout.
        """
        ink_rect_pointer = ffi.new("PangoRectangle *")
        logical_rect_pointer = ffi.new("PangoRectangle *")
        pango.pango_layout_get_extents(
            self._pointer,
            ink_rect_pointer,
            logical_rect_pointer
        )
        ink_rect = Rectangle.from_pointer(ink_rect_pointer)
        logical_rect = Rectangle.from_pointer(logical_rect_pointer)
        return ink_rect, logical_rect

    def get_size(self) -> Tuple[int, int]:
        """
        Determines the logical width and height of the layout in Pango units.
        This is simply a convenience function around get_extents().

        :return:
            a tuple containing the logical width and height, respectively.
        """
        width_pointer = ffi.new("int *")
        height_pointer = ffi.new("int *")
        pango.pango_layout_get_size(
            self._pointer,
            width_pointer,
            height_pointer
        )
        width = width_pointer[0]
        height = height_pointer[0]
        return width, height
