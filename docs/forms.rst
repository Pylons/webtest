Form handling
=============

Getting a form
--------------

If you have a single html form in your page, just use the ``.form`` attribute:

.. code-block:: python

    >>> res = app.get('/form.html')
    >>> form = res.form

You can use the form index if your html contains more than one form:

.. code-block:: python

    >>> form = res.forms[0]

Or the form id:

.. code-block:: python

    >>> form = res.forms['myform']

You can check form attributes:

.. code-block:: python

    >>> print(form.id)
    myform
    >>> print(form.action)
    /form-submit
    >>> print(form.method)
    POST

Filling a form
--------------

You can fill out and submit forms from your tests. Fields are a dict like
object:

.. code-block:: python

    >>> # dict of fields
    >>> form.fields.items() #doctest: +SKIP
    [(u'text', [<Text name="text">]), ..., (u'submit', [<Submit name="submit">])]

You can check the current value:

.. code-block:: python

    >>> print(form['text'].value)
    Foo

Then you fill it in fields:

.. code-block:: python

    >>> form['text'] = 'Bar'
    >>> # When names don't point to a single field:
    >>> form.set('text', 'Bar', index=0)

Field types
------------

Input and textarea fields
*************************

.. code-block:: python

    >>> print(form['textarea'].value)
    Some text
    >>> form['textarea'] = 'Some other text'

You can force the value of an hidden field::

    >>> form['hidden'].force_value('2')

Select fields
*************

Simple select:

.. code-block:: python

    >>> print(form['select'].value)
    option2
    >>> form['select'] = 'option1'

Select multiple:

.. code-block:: python

    >>> print(form['multiple'].value) # doctest: +SKIP
    ['option2', 'option3']
    >>> form['multiple'] = ['option1']

You can select an option by its text with ``.select()``:

.. code-block:: python

    >>> form['select'].select(text="Option 2")
    >>> print(form['select'].value)
    option2

For select multiple use ``.select_multiple()``:

.. code-block:: python

    >>> form['multiple'].select_multiple(texts=["Option 1", "Option 2"])
    >>> print(form['multiple'].value) # doctest: +SKIP
    ['option1', 'option2']

Select fields can only be set to valid values (i.e., values in an ``<option>``)
but you can also use ``.force_value()`` to enter values not present in an
option.

.. code-block:: python

    >>> form['select'].force_value(['optionX'])
    >>> form['multiple'].force_value(['optionX'])

Checkbox
********

.. autoclass:: Checkbox

You can check if the checkbox is checked and is value:

.. code-block:: python

    >>> print(form['checkbox'].checked)
    False
    >>> print(form['checkbox'].value)
    None

You can change the status with the value::

    >>> form['checkbox'] = True

Or with the checked attribute::

    >>> form['checkbox'].checked =True

If the checkbox is checked then you'll get the value::

    >>> print(form['checkbox'].checked)
    True
    >>> print(form['checkbox'].value)
    checkbox 1

If the checkbox has no value then it will be 'on' if you checked it::

    >>> print(form['checkbox2'].value)
    None
    >>> form['checkbox2'].checked = True
    >>> print(form['checkbox2'].value)
    on

If there are multiple checkboxes of the same name, you can assign a list to
that name to check all the checkboxes whose value is present in the list::

    >>> form['checkboxes'] = ['a', 'c']
    >>> print(form.get('checkboxes', index=0).value)
    a
    >>> print(form.get('checkboxes', index=1).value)
    None
    >>> print(form.get('checkboxes', index=2).value)
    c

Radio
*****

.. code-block:: python

    >>> print(form['radio'].value)
    Radio 2
    >>> form['radio'] = 'Radio 1'

File
****

You can deal with file upload by using the Upload class:

.. code-block:: python

    >>> from webtest import Upload
    >>> form['file'] = Upload('README.rst')
    >>> form['file'] = Upload('README.rst', b'data')
    >>> form['file'] = Upload('README.rst', b'data', 'text/x-rst')

Submit a form
--------------

Then you can submit the form:

.. code-block:: python

    >>> # Submit with no particular submit button pressed:
    >>> res = form.submit()
    >>> # Or submit a button:
    >>> res = form.submit('submit')
    >>> print(res)
    Response: 200 OK
    Content-Type: text/plain
    text=Bar
    ...
    submit=Submit

You can also select a specific submit button by its index:

.. code-block:: python

    >>> res = form.submit('submit', index=1)
    >>> print(res)
    Response: 200 OK
    Content-Type: text/plain
    ...
    submit=Submit 2

And you can select it by its value:

.. code-block:: python

    >>> res = form.submit('submit', value="Submit 2")
    >>> print(res)
    Response: 200 OK
    Content-Type: text/plain
    ...
    submit=Submit 2
