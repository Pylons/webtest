from webtest import _parse_attrs

def test_parse_attrs():
    assert _parse_attrs("href='foo'") == {'href': 'foo'}
    assert _parse_attrs('href="foo"') == {'href': 'foo'}
    assert _parse_attrs('href="foo" id="bar"') == {'href': 'foo', 'id': 'bar'}
    assert _parse_attrs('href="foo" id="bar"') == {'href': 'foo', 'id': 'bar'}
    assert _parse_attrs("href='foo' id=\"bar\" ") == {'href': 'foo', 'id': 'bar'}
    assert _parse_attrs("href='foo' id='bar' ") == {'href': 'foo', 'id': 'bar'}
