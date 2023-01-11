from pathlib import Path
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple

from parsy import Parser
from parsy import string
from parsy import success

from semdep.parsers.util import any_str
from semdep.parsers.util import consume_line
from semdep.parsers.util import line_number
from semdep.parsers.util import not_any
from semdep.parsers.util import safe_path_parse
from semdep.parsers.util import transitivity
from semgrep.semgrep_interfaces.semgrep_output_v1 import Ecosystem
from semgrep.semgrep_interfaces.semgrep_output_v1 import FoundDependency
from semgrep.semgrep_interfaces.semgrep_output_v1 import Pypi


comment = string(" ").many() >> string("#") >> not_any(["\n"])
newline = comment.optional() >> string("\n")

extra_info = not_any(["\\\\", "\n"])

package = not_any(["=", "<", ">", " ", "\n"])
version = not_any([";", " ", "\n"])


def dep(sep: "Parser[str]") -> "Parser[Tuple[str,str]]":
    return package.bind(
        lambda package: sep
        >> version.bind(
            lambda version: extra_info.optional() >> success((package, version))
        )
    )


manifest_dep = dep(any_str(["==", "<=", ">=", ">", "<"])) | package.map(
    lambda x: (x, "")
)

manifest = (
    (manifest_dep << newline.many()).map(lambda t: t[0]).many().map(lambda x: set(x))
)

hash = string("    --hash=sha256:") >> not_any([" ", "\n"])

hashes = hash.sep_by(string(" \\") >> newline.many())

empty_hashes: Dict[str, List[str]] = {}


def dep_hashes(
    manifest_deps: Optional[Set[str]],
) -> "Parser[Optional[FoundDependency]]":
    return (
        dep(string("==")).bind(
            lambda dep: line_number.bind(
                lambda line_number: string("\\").optional()
                >> newline
                >> hashes.map(lambda hashes: {"sha256": hashes})
                .optional(default=empty_hashes)
                .bind(
                    lambda hashes: success(
                        FoundDependency(
                            package=dep[0],
                            version=dep[1],
                            ecosystem=Ecosystem(Pypi()),
                            allowed_hashes=hashes,
                            transitivity=transitivity(manifest_deps, [dep[0]]),
                            line_number=line_number,
                        )
                    )
                )
            )
        )
        | consume_line
    )


def requirements(
    manifest_deps: Optional[Set[str]],
) -> "Parser[List[FoundDependency]]":
    return (
        (dep_hashes(manifest_deps) << newline.many())
        .many()
        .map(lambda xs: [x for x in xs if x])
    )


def parse_requirements(
    lockfile_path: Path, manifest_path: Optional[Path]
) -> List[FoundDependency]:
    manifest_deps = safe_path_parse(manifest_path, manifest)

    output = safe_path_parse(lockfile_path, requirements(manifest_deps))
    return output if output else []


manifest_text = """\
bunch==1.0.1 # foo
# foo
coverage==6.3.3
dominate==2.6.0
numpy==1.23.2
pandas #Comment
plotly
psutil==5.9.0
pylint<=2.13.9
pytest>=7.1.2
pytest-forked==1.4.0
pytest-xdist==2.5.0
tqdm==4.64.0
wcmatch==8.3
"""

text = r"""\
#
# This file is autogenerated by pip-compile with python 3.8
# To update, run:
#
#    pip-compile
#
astroid==2.11.5
    # via pylint
attrs==21.4.0
    # via pytest
bracex==2.2.1
    # via wcmatch
bunch==1.0.1
    # via -r requirements.in
coverage==6.3.3
    # via -r requirements.in
dill==0.3.4
    # via pylint
dominate==2.6.0
    # via -r requirements.in
execnet==1.9.0
    # via pytest-xdist
iniconfig==1.1.1
    # via pytest
isort==5.10.1
    # via pylint
lazy-object-proxy==1.7.1
    # via astroid
mccabe==0.6.1
    # via pylint
numpy==1.23.2
    # via
    #   -r requirements.in
    #   pandas
packaging==21.3
    # via pytest
pandas==1.4.2
    # via -r requirements.in
platformdirs==2.4.0
    # via pylint
plotly==5.8.0
    # via -r requirements.in
pluggy==1.0.0
    # via pytest
psutil==5.9.0
    # via -r requirements.in
py==1.11.0
    # via
    #   pytest
    #   pytest-forked
pylint==2.13.9
    # via -r requirements.in
pyparsing==3.0.7
    # via packaging
pytest==7.1.2
    # via
    #   -r requirements.in
    #   pytest-forked
    #   pytest-xdist
pytest-forked==1.4.0
    # via
    #   -r requirements.in
    #   pytest-xdist
pytest-xdist==2.5.0
    # via -r requirements.in
python-dateutil==2.8.2
    # via pandas
pytz==2021.3; python_version >= "3.6" and sys_platform == "darwin" \
    --hash=sha256:4f401444068d4ca8dc4a472b6de14b346e988af27af99c124d0478cb03da1d0c \
    --hash=sha256:c896ea1ca59b47d93777c7de092ca93f9ab7a00578f89805a2cea331ac98b545 \
    --hash=sha256:60b2f966701962747a6c3ad089c8be7a61376e77ce37fec5225aeb5bd0747e7f \
    --hash=sha256:4a30919f4ac52a2f8d7fd1c656b2a322396e42070f78dd6b884b5c0bd2b27576
    # via pandas
six==1.16.0
    # via python-dateutil
tenacity==8.0.1
    # via plotly
tomli==2.0.0 # Comment
    # via
    #   pylint
    #   pytest
tqdm==4.64.0; python_version >= "3.6" and sys_platform == "darwin" and platform_release >= "9.0" \
    --hash=sha256:c45207ffc5f583e9519561414298f713d299a6fe659ffff3d2a1554ae46111c6 \
    --hash=sha256:ceb1af4bb4da6347fb8a99c2ef5d88145b962fd87514fbf0aeca4717e584443c \
    --hash=sha256:a7d09ebc17fb7870edcab2ad30f56ab62bcabd069d1094557fb29f726ab19f83 \
    --hash=sha256:6fad2ce0a5f8cf7042716aa8b451c61416ae7a97165b6cc29cad4f2dce2de0fa
    # via -r requirements.in
wcmatch==8.3
    # via -r requirements.in
wrapt==1.13.3
    # via astroid

# The following packages are considered to be unsafe in a requirements file:
# setuptools
"""
