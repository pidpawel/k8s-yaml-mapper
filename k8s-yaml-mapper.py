#!/usr/bin/python3
import click
import yaml
from pprint import pprint
from typing import Dict, Any, Union, List

YamlObjectT = Dict[Any, Any]


def extract_namespace(source: YamlObjectT) -> str:
    return (
        source["metadata"]["namespace"]
        if "namespace" in source["metadata"]
        else "default"
    )


def extract_name(source: YamlObjectT) -> str:
    return source["metadata"]["name"]


def extract_kind(source: YamlObjectT) -> str:
    return source["kind"]


def create_parent_dictionaries(d: Dict, namespace: str, name: str, kind: str) -> None:
    if namespace not in d:
        d[namespace] = dict()
    if name not in d[namespace]:
        d[namespace][name] = dict()
    if kind not in d[namespace][name]:
        d[namespace][name][kind] = dict()


def compare_lists(a: List[YamlObjectT], b: List[YamlObjectT]) -> None:
    a_copy = a[:]

    for b_item in b:
        assert b_item in a_copy
        a_copy.remove(b_item)

    assert len(a_copy) == 0


def compare_files(source: str, destination: str, nested: bool) -> None:
    with open(source, "r") as source_file, open(destination, "r") as destination_file:
        source_objects = list(yaml.safe_load_all(source_file))
        destination_objects = list(yaml.safe_load_all(destination_file))

        assert len(destination_objects) == 1

        if nested:
            objects: List[YamlObjectT] = list()
            for namespace in destination_objects[0]:
                for name in destination_objects[0][namespace]:
                    for kind in destination_objects[0][namespace][name]:
                        objects.append(destination_objects[0][namespace][name][kind])

            compare_lists(source_objects, objects)
        else:
            compare_lists(source_objects, list(destination_objects[0].values()))


@click.command()
@click.argument("source", nargs=1)
@click.argument("destination", nargs=1)
@click.option(
    "-n",
    "--nested",
    is_flag=True,
    help="Create a multi-level mapping instead of a --separator concatednated string keys",
)
@click.option(
    "-s",
    "--separator",
    default=".",
    type=str,
    help="Use this separator when joining key elements",
)
@click.option(
    "--verify",
    "--no-verify",
    is_flag=True,
    default=True,
    help="Verify the files after conversion",
)
def k8s_yaml_mapper(
    source: str, destination: str, nested: bool, separator: str, verify: bool
) -> None:
    """Tool for converting YAML streams of k8s objects to single document YAML dictionaries with predictable paths.

    SOURCE file is expected to contain the YAML stream of k8s objects.
    DESTINATION file will have the resuting YAML dictionary written to."""
    with open(source, "r") as source_file, open(destination, "w") as destination_file:
        source_objects = yaml.safe_load_all(source_file)
        destination_objects: Dict[
            str, Union[YamlObjectT, Dict[str, Dict[str, YamlObjectT]]]
        ] = dict()

        for source_object in source_objects:
            object_namespace = extract_namespace(source_object)
            object_name = extract_name(source_object)
            object_kind = extract_kind(source_object)

            if nested:
                create_parent_dictionaries(
                    destination_objects, object_namespace, object_name, object_kind
                )
                destination_objects[object_namespace][object_name][
                    object_kind
                ] = source_object
            else:
                path = separator.join((object_namespace, object_name, object_kind))
                destination_objects[path] = source_object

        yaml.safe_dump(destination_objects, destination_file)

    if verify:
        compare_files(source=source, destination=destination, nested=nested)


if __name__ == "__main__":
    k8s_yaml_mapper()
