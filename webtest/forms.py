# -*- coding: utf-8 -*-
__doc__ = """Helpers to fill and submit forms"""
from webtest.compat import OrderedDict
from webtest import utils
import re


class Upload(object):
    """A file to upload::

        >>> Upload('filename.txt', 'data')
        <Upload "filename.txt">
        >>> Upload("README.txt")
        <Upload "README.txt">
    """
    def __init__(self, filename, content=None):
        self.filename = filename
        self.content = content

    def __iter__(self):
        yield self.filename
        if self.content:
            yield self.content

    def __repr__(self):
        return '<Upload "%s">' % self.filename


class Field(object):
    """Field object."""

    # Dictionary of field types (select, radio, etc) to classes
    classes = {}

    def __init__(self, form, tag, name, pos,
                 value=None, id=None, **attrs):
        self.form = form
        self.tag = tag
        self.name = name
        self.pos = pos
        self._value = value
        self.id = id
        self.attrs = attrs

    def value__set(self, value):
        self._value = value

    def force_value(self, value):
        """Like setting a value, except forces it even for, say, hidden
        fields.
        """
        self._value = value

    def __repr__(self):
        value = '<%s name="%s"' % (self.__class__.__name__, self.name)
        if self.id:
            value += ' id="%s"' % self.id
        return value + '>'


class NoValue(object):
    pass


class Select(Field):
    """Field representing ``<select>``"""

    def __init__(self, *args, **attrs):
        super(Select, self).__init__(*args, **attrs)
        self.options = []
        # Undetermined yet:
        self.selectedIndex = None
        # we have no forced value
        self._forced_value = NoValue

    def force_value(self, value):
        self._forced_value = value

    def value__set(self, value):
        if self._forced_value is not NoValue:
            self._forced_value = NoValue
        for i, (option, checked) in enumerate(self.options):
            if option == utils.stringify(value):
                self.selectedIndex = i
                break
        else:
            raise ValueError(
                "Option %r not found (from %s)"
                % (value, ', '.join(
                [repr(o) for o, c in self.options])))

    def value__get(self):
        if self._forced_value is not NoValue:
            return self._forced_value
        elif self.selectedIndex is not None:
            return self.options[self.selectedIndex][0]
        else:
            for option, checked in self.options:
                if checked:
                    return option
            else:
                if self.options:
                    return self.options[0][0]
                else:
                    return None

    value = property(value__get, value__set)

Field.classes['select'] = Select


class MultipleSelect(Field):
    """Field representing ``<select multiple="multiple">``"""

    def __init__(self, *args, **attrs):
        super(MultipleSelect, self).__init__(*args, **attrs)
        self.options = []
        # Undetermined yet:
        self.selectedIndices = []
        self._forced_values = []

    def force_value(self, values):
        self._forced_values = values
        self.selectedIndices = []

    def value__set(self, values):
        str_values = [utils.stringify(value) for value in values]
        self.selectedIndices = []
        for i, (option, checked) in enumerate(self.options):
            if option in str_values:
                self.selectedIndices.append(i)
                str_values.remove(option)
        if str_values:
            raise ValueError(
                "Option(s) %r not found (from %s)"
                % (', '.join(str_values),
                   ', '.join(
                        [repr(o) for o, c in self.options])))

    def value__get(self):
        selected_values = []
        if self.selectedIndices:
            selected_values = [self.options[i][0] \
                                    for i in self.selectedIndices]
        elif not self._forced_values:
            selected_values = []
            for option, checked in self.options:
                if checked:
                    selected_values.append(option)
        if self._forced_values:
            selected_values += self._forced_values

        if self.options and (not selected_values):
            selected_values = None
        return selected_values
    value = property(value__get, value__set)

Field.classes['multiple_select'] = MultipleSelect


class Radio(Select):
    """Field representing ``<input type="radio">``"""

    def value__get(self):
        if self.selectedIndex is not None:
            return self.options[self.selectedIndex][0]
        else:
            for option, checked in self.options:
                if checked:
                    return option
            else:
                return None

    value = property(value__get, Select.value__set)

Field.classes['radio'] = Radio


class Checkbox(Field):
    """Field representing ``<input type="checkbox">``"""

    def __init__(self, *args, **attrs):
        super(Checkbox, self).__init__(*args, **attrs)
        self._checked = 'checked' in attrs

    def value__set(self, value):
        self._checked = not not value

    def value__get(self):
        if self._checked:
            if self._value is None:
                return 'on'
            else:
                return self._value
        else:
            return None

    value = property(value__get, value__set)

    def checked__get(self):
        return bool(self._checked)

    def checked__set(self, value):
        self._checked = not not value

    checked = property(checked__get, checked__set)

Field.classes['checkbox'] = Checkbox


class Text(Field):
    """Field representing ``<input type="text">``"""

    def value__get(self):
        if self._value is None:
            return ''
        else:
            return self._value

    value = property(value__get, Field.value__set)

Field.classes['text'] = Text


class File(Field):
    """Field representing ``<input type="file">``"""

    ## FIXME: This doesn't actually handle file uploads and enctype
    def value__get(self):
        if self._value is None:
            return ''
        else:
            return self._value

    value = property(value__get, Field.value__set)

Field.classes['file'] = File


class Textarea(Text):
    """Field representing ``<textarea>``"""

Field.classes['textarea'] = Textarea


class Hidden(Text):
    """Field representing ``<input type="hidden">``"""

Field.classes['hidden'] = Hidden


class Submit(Field):
    """Field representing ``<input type="submit">`` and ``<button>``"""

    def value__get(self):
        return None

    def value__set(self,value):
        raise AttributeError(
            "You cannot set the value of the <%s> field %r"
            % (self.tag, self.name))
 
    value = property(value__get, value__set)

    def value_if_submitted(self):
        return self._value

Field.classes['submit'] = Submit

Field.classes['button'] = Submit

Field.classes['image'] = Submit


class Form(object):
    """This object represents a form that has been found in a page.
    This has a couple useful attributes:

    ``text``:
        the full HTML of the form.

    ``action``:
        the relative URI of the action.

    ``method``:
        the method (e.g., ``'GET'``).

    ``id``:
        the id, or None if not given.

    ``fields``:
        a dictionary of fields, each value is a list of fields by
        that name.  ``<input type=\"radio\">`` and ``<select>`` are
        both represented as single fields with multiple options.
    """

    # @@: This really should be using Mechanize/ClientForm or
    # something...

    _tag_re = re.compile(r'<(/?)([a-z0-9_\-]*)([^>]*?)>', re.I)
    _label_re = re.compile(
            '''<label\s+(?:[^>]*)for=(?:"|')([a-z0-9_\-]+)(?:"|')(?:[^>]*)>''',
            re.I)

    FieldClass = Field

    def __init__(self, response, text):
        self.response = response
        self.text = text
        self._parse_fields()
        self._parse_action()

    def _parse_fields(self):
        in_select = None
        in_textarea = None
        fields = OrderedDict()
        field_order = []
        for match in self._tag_re.finditer(self.text):
            end = match.group(1) == '/'
            tag = match.group(2).lower()
            if tag not in ('input', 'select', 'option', 'textarea',
                           'button'):
                continue
            if tag == 'select' and end:
                assert in_select, (
                    '%r without starting select' % match.group(0))
                in_select = None
                continue
            if tag == 'textarea' and end:
                assert in_textarea, (
                    "</textarea> with no <textarea> at %s" % match.start())
                in_textarea[0].value = utils.unescape_html(
                                    self.text[in_textarea[1]:match.start()])
                in_textarea = None
                continue
            if end:
                continue
            attrs = utils.parse_attrs(match.group(3))
            if 'name' in attrs:
                name = attrs.pop('name')
            else:
                name = None
            if tag == 'option':
                in_select.options.append((attrs.get('value'),
                                          'selected' in attrs))
                continue
            if tag == 'input' and attrs.get('type') == 'radio':
                field = fields.get(name)
                if not field:
                    field = self.FieldClass.classes['radio'](
                                       self, tag, name, match.start(), **attrs)
                    fields.setdefault(name, []).append(field)
                    field_order.append((name, field))
                else:
                    field = field[0]
                    assert isinstance(field, self.FieldClass.classes['radio'])
                field.options.append((attrs.get('value'),
                                      'checked' in attrs))
                continue
            tag_type = tag
            if tag == 'input':
                tag_type = attrs.get('type', 'text').lower()
            if tag_type == "select" and attrs.get("multiple"):
                FieldClass = self.FieldClass.classes.get("multiple_select",
                                                         self.FieldClass)
            else:
                FieldClass = self.FieldClass.classes.get(tag_type,
                                                         self.FieldClass)
            field = FieldClass(self, tag, name, match.start(), **attrs)
            if tag == 'textarea':
                assert not in_textarea, (
                    "Nested textareas: %r and %r"
                    % (in_textarea, match.group(0)))
                in_textarea = field, match.end()
            elif tag == 'select':
                assert not in_select, (
                    "Nested selects: %r and %r"
                    % (in_select, match.group(0)))
                in_select = field
            fields.setdefault(name, []).append(field)
            field_order.append((name, field))
        self.field_order = field_order
        self.fields = fields

    def _parse_action(self):
        self.action = None
        for match in self._tag_re.finditer(self.text):
            end = match.group(1) == '/'
            tag = match.group(2).lower()
            if tag != 'form':
                continue
            if end:
                break
            attrs = utils.parse_attrs(match.group(3))
            self.action = attrs.get('action', '')
            self.method = attrs.get('method', 'GET')
            self.id = attrs.get('id')
            self.enctype = attrs.get('enctype',
                                     'application/x-www-form-urlencoded')
        else:
            assert 0, "No </form> tag found"
        assert self.action is not None, (
            "No <form> tag found")

    def __setitem__(self, name, value):
        """Set the value of the named field. If there is 0 or multiple fields
        by that name, it is an error.

        Setting the value of a ``<select>`` selects the given option (and
        confirms it is an option). Setting radio fields does the same.
        Checkboxes get boolean values. You cannot set hidden fields or buttons.

        Use ``.set()`` if there is any ambiguity and you must provide an index.
        """
        fields = self.fields.get(name)
        assert fields is not None, (
            "No field by the name %r found (fields: %s)"
            % (name, ', '.join(map(repr, self.fields.keys()))))
        assert len(fields) == 1, (
            "Multiple fields match %r: %s"
            % (name, ', '.join(map(repr, fields))))
        fields[0].value = value

    def __getitem__(self, name):
        """Get the named field object (ambiguity is an error)."""
        fields = self.fields.get(name)
        assert fields is not None, (
            "No field by the name %r found" % name)
        assert len(fields) == 1, (
            "Multiple fields match %r: %s"
            % (name, ', '.join(map(repr, fields))))
        return fields[0]

    def lint(self):
        """Check that the html is valid:

        - each field must have an id
        - each field must have a label
        """
        labels = self._label_re.findall(self.text)
        for name, fields in self.fields.items():
            for field in fields:
                if not isinstance(field, (Submit, Hidden)):
                    if not field.id:
                        raise AttributeError(
                             "%r as no id attribute" % field)
                    elif field.id not in labels:
                        raise AttributeError(
                             "%r as no associated label" % field)

    def set(self, name, value, index=None):
        """Set the given name, using ``index`` to disambiguate."""
        if index is None:
            self[name] = value
        else:
            fields = self.fields.get(name)
            assert fields is not None, (
                "No fields found matching %r" % name)
            field = fields[index]
            field.value = value

    def get(self, name, index=None, default=utils.NoDefault):
        """Get the named/indexed field object, or ``default`` if no field is
        found. Throws an AssertionError if no field is found and no default was given.
        """
        fields = self.fields.get(name)
        if fields is None:
            if default is utils.NoDefault:
                raise AssertionError(
                    "No fields found matching %r (and no default given)" 
                    % name)
            return default
        if index is None:
            return self[name]
        return fields[index]

    def select(self, name, value, index=None):
        """Like ``.set()``, except also confirms the target is a ``<select>``.
        """
        field = self.get(name, index=index)
        assert isinstance(field, Select)
        field.value = value

    def submit(self, name=None, index=None, **args):
        """Submits the form.  If ``name`` is given, then also select that
        button (using ``index`` to disambiguate)``.

        Any extra keyword arguments are passed to the ``.get()`` or
        ``.post()`` method.

        Returns a :class:`webtest.TestResponse` object.
        """
        fields = self.submit_fields(name, index=index)
        if self.method.upper() != "GET":
            args.setdefault("content_type",  self.enctype)
        return self.response.goto(self.action, method=self.method,
                                  params=fields, **args)

    def upload_fields(self):
        """Return a list of file field tuples of the form:
            (field name, file name)

        or:

            (field name, file name, file contents).
        """
        uploads = []
        for name, fields in self.fields.items():
            for field in fields:
                if isinstance(field, File) and field.value:
                    uploads.append([name] + list(field.value))
        return uploads

    def submit_fields(self, name=None, index=None):
        """Return a list of ``[(name, value), ...]`` for the current state of
        the form.
        """
        submit = []
        # Use another name here so we can keep function param the same for BWC.
        submit_name = name
        if index is None:
            index = 0
        # This counts all fields with the submit name not just submit fields.
        current_index = 0
        for name, field in self.field_order:
            if name is None:
                continue
            if submit_name is not None and name == submit_name:
                if current_index == index:
                    submit.append((name, field.value_if_submitted()))
                current_index += 1
            else:
                value = field.value
                if value is None:
                    continue
                if isinstance(field, File):
                    submit.append((name, field))
                    continue
                if isinstance(value, list):
                    for item in value:
                        submit.append((name, item))
                else:
                    submit.append((name, value))
        return submit

    def __repr__(self):
        value = '<Form'
        if self.id:
            value += ' id=%r' % str(self.id)
        return value + ' />'
