#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .dxf_codes import name_to_dxf_code


class ConverterError(Exception):
    pass

DXF_CONDITIONAL_OPERATOR = -4

def convert_tree(node):
    conditions = flatten_selection_tree(node, [])
    return convert_to_filter_type_and_data(conditions)


def flatten_selection_tree(node, result, level=0):

    def show(*items):
        if level:
            print '  ' * level,
        print ' '.join(map(unicode, items))

    connector = node.connector if not node.negated else 'NOT'
    operator = '<%s' % connector
    show(operator)
    result.append((DXF_CONDITIONAL_OPERATOR, operator))
    for child in node.children:
        if isinstance(child, tuple):
            show(child)
            result.append(child)
        else:
            flatten_selection_tree(child, result, level + 1)
    operator = '%s>' % connector
    show(operator)
    result.append((DXF_CONDITIONAL_OPERATOR, operator))
    return result


def convert_condition_to_dxf_codes(condition):
    name, value = condition
    if isinstance(name, int):
        yield name, value
        return
    if '__' in name:
        name, rel_operator  = name.split('__')
        operator = rel_operators_map.get(rel_operator)
        if operator is None:
            raise ConverterError("Unknown relational operator %r" % rel_operator)
        yield DXF_CONDITIONAL_OPERATOR, operator
    try:
        yield name_to_dxf_code[name], value
    except KeyError:
        raise ConverterError("Unknown field %r" % name)


def convert_to_filter_type_and_data(conditions):
    codes = []
    data = []
    for cond in conditions:
        for code, value in convert_condition_to_dxf_codes(cond):
            codes.append(code)
            data.append(value)
    return codes, data


rel_operators_map = {
    'eq': '=',
    'ne': '!=',
    'any': '*',
    'all': '*',
    'lt': '<',
    'lte': '<=',
    'gt': '>',
    'gte': '>=',
    'and': '&',
    'mand': '&=',
}