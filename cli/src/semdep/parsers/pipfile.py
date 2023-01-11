from collections import defaultdict
from typing import Dict
from typing import List
from typing import Optional

from semdep.parsers.poetry import manifest
from semdep.parsers.util import json_doc
from semdep.parsers.util import transitivity
from semgrep.semgrep_interfaces.semgrep_output_v1 import Ecosystem
from semgrep.semgrep_interfaces.semgrep_output_v1 import FoundDependency
from semgrep.semgrep_interfaces.semgrep_output_v1 import Pypi
from semgrep.verbose_logging import getLogger


logger = getLogger(__name__)


def parse_pipfile(
    lockfile_text: str, manifest_text: Optional[str]
) -> List[FoundDependency]:
    manifest_deps = manifest.parse(manifest_text) if manifest_text else None

    lockfile_json = json_doc.parse(lockfile_text).as_dict()
    deps = lockfile_json["default"].as_dict()

    def extract_pipfile_hashes(
        hashes: List[str],
    ) -> Dict[str, List[str]]:
        output = defaultdict(list)
        for h in hashes:
            algorithm = h.split(":")[0]
            rest = h[len(algorithm) + 1 :]  # pipfile is already in base16
            output[algorithm].append(rest.lower())
        return output

    output = []
    for package, dep_json in deps.items():
        fields = dep_json.as_dict()
        if "version" not in fields:
            logger.info(f"no version for dependency: {package}")
            continue
        version = fields["version"].as_str()
        version = version.replace("==", "")
        output.append(
            FoundDependency(
                package=package,
                version=version,
                ecosystem=Ecosystem(Pypi()),
                resolved_url=None,
                allowed_hashes=extract_pipfile_hashes(
                    [h.as_str() for h in fields["hashes"].as_list()]
                )
                if "hashes" in fields
                else {},
                transitivity=transitivity(manifest_deps, [package]),
                line_number=dep_json.line_number,
            )
        )
    return output
