#!/usr/bin/env python3
#  Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import pytest

from fruit_test_common import *

COMMON_DEFINITIONS = '''
    #include "test_common.h"

    struct X;
    struct Y;
    struct Z;

    struct Annotation1 {};
    using XAnnot1 = fruit::Annotated<Annotation1, X>;
    using YAnnot1 = fruit::Annotated<Annotation1, Y>;
    using ZAnnot1 = fruit::Annotated<Annotation1, Z>;

    struct Annotation2 {};
    using XAnnot2 = fruit::Annotated<Annotation2, X>;
    using YAnnot2 = fruit::Annotated<Annotation2, Y>;
    using ZAnnot2 = fruit::Annotated<Annotation2, Z>;

    struct Annotation3 {};
    '''

CONSTRUCTOR_BINDING=(
    '',
    '.registerConstructor<XAnnot()>()')
INTERFACE_BINDING=(
    '''
        struct Y : public X {};
    ''',
    '''
        .bind<XAnnot, YAnnot>()
        .registerConstructor<YAnnot()>()
    ''')
INTERFACE_BINDING2=(
    '''
        struct Y2 : public X {};
    ''',
    '''
        .bind<XAnnot, Y2Annot>()
        .registerConstructor<Y2Annot()>()
    ''')
INSTALL=(
    '''
        fruit::Component<XAnnot> getParentComponent() {
          return fruit::createComponent()
            .registerConstructor<XAnnot()>();
        }
    ''',
    '.install(getParentComponent)')
INSTALL2=(
    '''
        fruit::Component<XAnnot> getParentComponent2() {
          return fruit::createComponent()
            .registerConstructor<XAnnot()>();
        }
    ''',
    '.install(getParentComponent2)')
OLD_STYLE_INSTALL=(
    '''
        fruit::Component<XAnnot> getParentComponent() {
          return fruit::createComponent()
            .registerConstructor<XAnnot()>();
        }
    ''',
    '.install(getParentComponent())')
OLD_STYLE_INSTALL2=(
    '''
        fruit::Component<XAnnot> getParentComponent2() {
          return fruit::createComponent()
            .registerConstructor<XAnnot()>();
        }
    ''',
    '.install(getParentComponent2())')

@pytest.mark.parametrize(
    'binding1_preparation,binding1,binding2_preparation,binding2',
    [
        CONSTRUCTOR_BINDING + CONSTRUCTOR_BINDING,
        CONSTRUCTOR_BINDING + INTERFACE_BINDING,
        INTERFACE_BINDING + CONSTRUCTOR_BINDING,
        INTERFACE_BINDING + INTERFACE_BINDING2,
        INSTALL + CONSTRUCTOR_BINDING,
        INSTALL + INTERFACE_BINDING,
    ],
    ids= [
        'CONSTRUCTOR_BINDING + CONSTRUCTOR_BINDING',
        'CONSTRUCTOR_BINDING + INTERFACE_BINDING',
        'INTERFACE_BINDING + CONSTRUCTOR_BINDING',
        'INTERFACE_BINDING + INTERFACE_BINDING2',
        'INSTALL + CONSTRUCTOR_BINDING',
        'INSTALL + INTERFACE_BINDING',
    ])
@pytest.mark.parametrize('XAnnot,YAnnot,Y2Annot', [
    ('X', 'Y', 'Y2'),
    ('fruit::Annotated<Annotation1, X>', 'fruit::Annotated<Annotation2, Y>', 'fruit::Annotated<Annotation3, Y2>'),
])
def test_clash_with_binding(binding1_preparation, binding1, binding2_preparation, binding2, XAnnot, YAnnot, Y2Annot):
    source = '''
        struct X{};

        %s
        %s

        fruit::Component<XAnnot> getComponent() {
          return fruit::createComponent()
              %s
              %s;
        }

        ''' % (binding1_preparation, binding2_preparation, binding1, binding2)
    expect_compile_error(
        'TypeAlreadyBoundError<XAnnot>',
        'Trying to bind C but it is already bound.',
        COMMON_DEFINITIONS,
        source,
        locals())

@pytest.mark.parametrize(
    'binding1_preparation,binding1,binding2_preparation,binding2',
    [
        OLD_STYLE_INSTALL + CONSTRUCTOR_BINDING,
        OLD_STYLE_INSTALL + INTERFACE_BINDING,
    ],
    ids= [
        'OLD_STYLE_INSTALL + CONSTRUCTOR_BINDING',
        'OLD_STYLE_INSTALL + INTERFACE_BINDING',
    ])
@pytest.mark.parametrize('XAnnot,YAnnot,Y2Annot', [
    ('X', 'Y', 'Y2'),
    ('fruit::Annotated<Annotation1, X>', 'fruit::Annotated<Annotation2, Y>', 'fruit::Annotated<Annotation3, Y2>'),
])
def test_clash_with_binding_old_style_install(
        binding1_preparation, binding1, binding2_preparation, binding2, XAnnot, YAnnot, Y2Annot):
    source = '''
        struct X{};

        %s
        %s

        fruit::Component<XAnnot> getComponent() {
          return fruit::createComponent()
              %s
              %s;
        }

        ''' % (binding1_preparation, binding2_preparation, binding1, binding2)
    expect_compile_error(
        'TypeAlreadyBoundError<XAnnot>',
        'Trying to bind C but it is already bound.',
        COMMON_DEFINITIONS,
        source,
        locals(),
        ignore_deprecation_warnings=True)

@pytest.mark.parametrize(
    'binding1_preparation,binding1,binding2_preparation,binding2',
    [
        CONSTRUCTOR_BINDING + INSTALL,
        INTERFACE_BINDING + INSTALL,
        INSTALL + INSTALL2,
    ],
    ids = [
        'CONSTRUCTOR_BINDING + INSTALL',
        'INTERFACE_BINDING + INSTALL',
        'INSTALL + INSTALL2',
    ])
@pytest.mark.parametrize('XAnnot,YAnnot,Y2Annot', [
    ('X', 'Y', 'Y2'),
    ('fruit::Annotated<Annotation1, X>', 'fruit::Annotated<Annotation2, Y>', 'fruit::Annotated<Annotation3, Y2>'),
])
def test_clash_with_install(
        binding1_preparation, binding1, binding2_preparation, binding2, XAnnot, YAnnot, Y2Annot):
    source = '''
        struct X{};

        %s
        %s

        fruit::Component<XAnnot> getComponent() {
          return fruit::createComponent()
              %s
              %s;
        }
        ''' % (binding1_preparation, binding2_preparation, binding1, binding2)
    expect_compile_error(
        'DuplicateTypesInComponentError<XAnnot>',
        'The installed component provides some types that are already provided by the current component.',
        COMMON_DEFINITIONS,
        source,
        locals())

@pytest.mark.parametrize(
    'binding1_preparation,binding1,binding2_preparation,binding2',
    [
        CONSTRUCTOR_BINDING + OLD_STYLE_INSTALL,
        INTERFACE_BINDING + OLD_STYLE_INSTALL,
        OLD_STYLE_INSTALL + OLD_STYLE_INSTALL2,
        INSTALL + OLD_STYLE_INSTALL2,
        OLD_STYLE_INSTALL + INSTALL2,
    ],
    ids = [
        'CONSTRUCTOR_BINDING + OLD_STYLE_INSTALL',
        'INTERFACE_BINDING + OLD_STYLE_INSTALL',
        'OLD_STYLE_INSTALL + OLD_STYLE_INSTALL2',
        'INSTALL + OLD_STYLE_INSTALL2',
        'OLD_STYLE_INSTALL + INSTALL2',
    ])
@pytest.mark.parametrize('XAnnot,YAnnot,Y2Annot', [
    ('X', 'Y', 'Y2'),
    ('fruit::Annotated<Annotation1, X>', 'fruit::Annotated<Annotation2, Y>', 'fruit::Annotated<Annotation3, Y2>'),
])
def test_clash_with_install_old_style_install(
        binding1_preparation, binding1, binding2_preparation, binding2, XAnnot, YAnnot, Y2Annot):
    source = '''
        struct X{};

        %s
        %s

        fruit::Component<XAnnot> getComponent() {
          return fruit::createComponent()
              %s
              %s;
        }
        ''' % (binding1_preparation, binding2_preparation, binding1, binding2)
    expect_compile_error(
        'DuplicateTypesInComponentError<XAnnot>',
        'The installed component provides some types that are already provided by the current component.',
        COMMON_DEFINITIONS,
        source,
        locals(),
        ignore_deprecation_warnings=True)

CONSTRUCTOR_BINDING_ANNOT1=(
    '',
    '.registerConstructor<XAnnot1()>()')
CONSTRUCTOR_BINDING_ANNOT2=(
    '',
    '.registerConstructor<XAnnot2()>()')
INTERFACE_BINDING_ANNOT1=(
    '''
        struct Y : public X {};
    ''',
    '''
        .bind<XAnnot1, YAnnot1>()
        .registerConstructor<YAnnot1()>()
    ''')
INTERFACE_BINDING_ANNOT2=(
    '''
        struct Z : public X {};
    ''',
    '''
        .bind<XAnnot2, ZAnnot2>()
        .registerConstructor<ZAnnot2()>()
    ''')
INSTALL_ANNOT1=(
    '''
        fruit::Component<XAnnot1> getParentComponent1() {
          return fruit::createComponent()
            .registerConstructor<XAnnot1()>();
        }
    ''',
    '.install(getParentComponent1)')
INSTALL_ANNOT2=(
    '''
        fruit::Component<XAnnot2> getParentComponent2() {
          return fruit::createComponent()
            .registerConstructor<XAnnot2()>();
        }
    ''',
    '.install(getParentComponent2)')
OLD_STYLE_INSTALL_ANNOT1=(
    '''
        fruit::Component<XAnnot1> getParentComponent1() {
          return fruit::createComponent()
            .registerConstructor<XAnnot1()>();
        }
    ''',
    '.install(getParentComponent1())')
OLD_STYLE_INSTALL_ANNOT2=(
    '''
        fruit::Component<XAnnot2> getParentComponent2() {
          return fruit::createComponent()
            .registerConstructor<XAnnot2()>();
        }
    ''',
    '.install(getParentComponent2())')

@pytest.mark.parametrize(
    'binding1_preparation,binding1,binding2_preparation,binding2',
    [
        CONSTRUCTOR_BINDING_ANNOT1 + CONSTRUCTOR_BINDING_ANNOT2,
        CONSTRUCTOR_BINDING_ANNOT1 + INTERFACE_BINDING_ANNOT2,
        INTERFACE_BINDING_ANNOT1 + CONSTRUCTOR_BINDING_ANNOT2,
        INTERFACE_BINDING_ANNOT1 + INTERFACE_BINDING_ANNOT2,
        INSTALL_ANNOT1 + CONSTRUCTOR_BINDING_ANNOT2,
        INSTALL_ANNOT1 + INTERFACE_BINDING_ANNOT2,
        CONSTRUCTOR_BINDING_ANNOT1 + INSTALL_ANNOT2,
        INTERFACE_BINDING_ANNOT1 + INSTALL_ANNOT2,
        INSTALL_ANNOT1 + INSTALL_ANNOT2,
    ],
    ids=[
        'CONSTRUCTOR_BINDING_ANNOT1 + CONSTRUCTOR_BINDING_ANNOT2',
        'CONSTRUCTOR_BINDING_ANNOT1 + INTERFACE_BINDING_ANNOT2',
        'INTERFACE_BINDING_ANNOT1 + CONSTRUCTOR_BINDING_ANNOT2',
        'INTERFACE_BINDING_ANNOT1 + INTERFACE_BINDING_ANNOT2',
        'INSTALL_ANNOT1 + CONSTRUCTOR_BINDING_ANNOT2',
        'INSTALL_ANNOT1 + INTERFACE_BINDING_ANNOT2',
        'CONSTRUCTOR_BINDING_ANNOT1 + INSTALL_ANNOT2',
        'INTERFACE_BINDING_ANNOT1 + INSTALL_ANNOT2',
        'INSTALL_ANNOT1 + INSTALL_ANNOT2',
    ])
def test_no_clash_with_different_annotations(binding1_preparation, binding1, binding2_preparation, binding2):
    source = '''
        struct X {};

        %s
        %s

        fruit::Component<XAnnot1, XAnnot2> getComponent() {
          return fruit::createComponent()
              %s
              %s;
        }

        int main() {
            fruit::Injector<XAnnot1, XAnnot2> injector(getComponent());
            injector.get<XAnnot1>();
            injector.get<XAnnot2>();
        }
        ''' % (binding1_preparation, binding2_preparation, binding1, binding2)
    expect_success(
        COMMON_DEFINITIONS,
        source)

@pytest.mark.parametrize(
    'binding1_preparation,binding1,binding2_preparation,binding2',
    [
        OLD_STYLE_INSTALL_ANNOT1 + CONSTRUCTOR_BINDING_ANNOT2,
        OLD_STYLE_INSTALL_ANNOT1 + INTERFACE_BINDING_ANNOT2,
        CONSTRUCTOR_BINDING_ANNOT1 + OLD_STYLE_INSTALL_ANNOT2,
        INTERFACE_BINDING_ANNOT1 + OLD_STYLE_INSTALL_ANNOT2,
        OLD_STYLE_INSTALL_ANNOT1 + INSTALL_ANNOT2,
        INSTALL_ANNOT1 + OLD_STYLE_INSTALL_ANNOT2,
        OLD_STYLE_INSTALL_ANNOT1 + OLD_STYLE_INSTALL_ANNOT2,
    ],
    ids=[
        'OLD_STYLE_INSTALL_ANNOT1 + CONSTRUCTOR_BINDING_ANNOT2',
        'OLD_STYLE_INSTALL_ANNOT1 + INTERFACE_BINDING_ANNOT2',
        'CONSTRUCTOR_BINDING_ANNOT1 + OLD_STYLE_INSTALL_ANNOT2',
        'INTERFACE_BINDING_ANNOT1 + OLD_STYLE_INSTALL_ANNOT2',
        'OLD_STYLE_INSTALL_ANNOT1 + INSTALL_ANNOT2',
        'INSTALL_ANNOT1 + OLD_STYLE_INSTALL_ANNOT2',
        'OLD_STYLE_INSTALL_ANNOT1 + OLD_STYLE_INSTALL_ANNOT2',
    ])
def test_no_clash_with_different_annotations_old_style_install(binding1_preparation, binding1, binding2_preparation, binding2):
    source = '''
        struct X {};

        %s
        %s

        fruit::Component<XAnnot1, XAnnot2> getComponent() {
          return fruit::createComponent()
              %s
              %s;
        }

        int main() {
            fruit::Injector<XAnnot1, XAnnot2> injector(getComponent());
            injector.get<XAnnot1>();
            injector.get<XAnnot2>();
        }
        ''' % (binding1_preparation, binding2_preparation, binding1, binding2)
    expect_success(
        COMMON_DEFINITIONS,
        source,
        ignore_deprecation_warnings=True)

@pytest.mark.parametrize('XAnnot', [
    'X',
    'fruit::Annotated<Annotation1, X>',
])
def test_during_component_merge(XAnnot):
    source = '''
        struct X {};

        fruit::Component<XAnnot> getComponent() {
          return fruit::createComponent()
            .registerConstructor<XAnnot()>();
        }

        void f() {
          fruit::NormalizedComponent<XAnnot> nc(getComponent());
          fruit::Injector<XAnnot> injector(nc, getComponent());
          (void) injector;
        }
        '''
    expect_compile_error(
        'DuplicateTypesInComponentError<XAnnot>',
        'The installed component provides some types that are already provided',
        COMMON_DEFINITIONS,
        source,
        locals())

def test_during_component_merge_with_different_annotation_ok():
    source = '''
        struct X {};

        fruit::Component<XAnnot1> getComponent1() {
          return fruit::createComponent()
            .registerConstructor<XAnnot1()>();
        }

        fruit::Component<XAnnot2> getComponent2() {
          return fruit::createComponent()
            .registerConstructor<XAnnot2()>();
        }

        int main() {
          fruit::NormalizedComponent<XAnnot1> nc(getComponent1());
          fruit::Injector<XAnnot1, XAnnot2> injector(nc, getComponent2());
          injector.get<XAnnot1>();
          injector.get<XAnnot2>();
        }
        '''
    expect_success(
        COMMON_DEFINITIONS,
        source)

@pytest.mark.parametrize('XAnnot,XAnnotRegex', [
    ('X', '(struct )?X'),
    ('fruit::Annotated<Annotation1, X>', '(struct )?fruit::Annotated<(struct )?Annotation1, ?(struct )?X>'),
])
def test_bind_instance_and_bind_instance_runtime(XAnnot, XAnnotRegex):
    source = '''
        struct X {};

        fruit::Component<> getComponentForInstanceHelper() {
          // Note: don't do this in real code, leaks memory.
          return fruit::createComponent()
            .bindInstance<XAnnot, X>(*(new X()));
        }
        
        fruit::Component<XAnnot> getComponentForInstance() {
          // Note: don't do this in real code, leaks memory.
          return fruit::createComponent()
            .install(getComponentForInstanceHelper)
            .bindInstance<XAnnot, X>(*(new X()));
        }

        int main() {
          fruit::Injector<XAnnot> injector(getComponentForInstance());
          injector.get<XAnnot>();
        }
        '''
    expect_runtime_error(
        'Fatal injection error: the type XAnnotRegex was provided more than once, with different bindings.',
        COMMON_DEFINITIONS,
        source,
        locals())

@pytest.mark.parametrize('XAnnot,XAnnotRegex', [
    ('X', '(struct )?X'),
    ('fruit::Annotated<Annotation1, X>', '(struct )?fruit::Annotated<(struct )?Annotation1, ?(struct )?X>'),
])
def test_bind_instance_and_binding_runtime(XAnnot, XAnnotRegex):
    source = '''
        struct X {};

        fruit::Component<> getComponentForInstanceHelper(X* x) {
          return fruit::createComponent()
            .bindInstance<XAnnot, X>(*x);
        }
        
        fruit::Component<XAnnot> getComponentForInstance(X& x) {
          return fruit::createComponent()
            .install(getComponentForInstanceHelper, &x)
            .registerConstructor<XAnnot()>();
        }

        int main() {
          X x;
          fruit::Injector<XAnnot> injector(getComponentForInstance(x));
          injector.get<XAnnot>();
        }
        '''
    expect_runtime_error(
        'Fatal injection error: the type XAnnotRegex was provided more than once, with different bindings.',
        COMMON_DEFINITIONS,
        source,
        locals())

@pytest.mark.parametrize('XAnnot', [
    'X',
    'fruit::Annotated<Annotation1, X>',
])
def test_during_component_merge_consistent_ok(XAnnot):
    source = '''
        struct X : public ConstructionTracker<X> {
          using Inject = X();
        };

        fruit::Component<XAnnot> getComponent() {
          return fruit::createComponent();
        }

        int main() {
          fruit::NormalizedComponent<> normalizedComponent(getComponent());
          fruit::Injector<XAnnot> injector(normalizedComponent, getComponent());

          Assert(X::num_objects_constructed == 0);
          injector.get<XAnnot>();
          Assert(X::num_objects_constructed == 1);
        }
        '''
    expect_success(
        COMMON_DEFINITIONS,
        source,
        locals())

if __name__== '__main__':
    main(__file__)
