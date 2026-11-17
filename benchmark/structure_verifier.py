"""Coordinate verification after xTB, using pinned MAPPA and explicit stereo gates.

MAPPA fixes one atom correspondence for stereo checks. Coarse ligand geometry
compares angle profiles within chemical site-pair classes; it is not a general
metal-chirality or full spatial-correspondence test. Whole-molecule RMSD and
ordinary rotatable-bond torsions are not acceptance criteria. All atom indices in the
API and diagnostics are zero-based reference indices.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from importlib import metadata
from itertools import combinations
import json
import math
import time

import networkx as nx
import numpy as np

MAPPA_COMMIT = "2f9762e1e09801e619cfd537abf3798ae8b0f3de"
VERIFIER_VERSION = "moldraft.stereochemistry/v18"


class VerificationUnresolved(RuntimeError):
    """A resource limit or reference ambiguity prevented a chemical verdict."""


class ReferenceConstraintError(ValueError):
    """An explicitly required reference configuration is undefined."""


@dataclass(frozen=True)
class VerificationPolicy:
    graph_floor: float = 0.15
    covalent_floor: float = 0.40
    double_bond_floor: float = 1.50
    bond_change: float = 0.5
    metal_bond_change: float = 0.3
    # Dimensionless determinant: insensitive to molecule size and units.
    volume_tolerance: float = 0.02
    projection_tolerance: float = 0.10
    # Operational gross-geometry tolerances, not universal chemical boundaries.
    coordination_angle_rms_deg: float = 20.0
    coordination_angle_max_deg: float = 60.0
    # Reference contacts use graph_floor. Retention has a lower floor so
    # borderline WBO fluctuations do not create artificial site loss.
    coordination_retention_floor: float = 0.10
    seed_count: int = 3
    branch_limit: int = 10000

    def __post_init__(self):
        for key, value in asdict(self).items():
            if not math.isfinite(value) or value <= 0:
                raise ValueError(f"{key} must be finite and positive")
        for key in ("seed_count", "branch_limit"):
            if type(getattr(self, key)) is not int:
                raise ValueError(f"{key} must be an integer")


def provenance(policy=VerificationPolicy()):
    """Reject an accidentally imported old/editable mapper; record its source."""
    dist = metadata.distribution("mappa")
    direct = json.loads(dist.read_text("direct_url.json") or "{}")
    commit = direct.get("vcs_info", {}).get("commit_id")
    if commit != MAPPA_COMMIT:
        raise RuntimeError(
            f"MAPPA must be installed at {MAPPA_COMMIT}; found {commit!r}. "
            "Install benchmark/requirements-current.txt.")
    return {"schema": VERIFIER_VERSION, "mappa_version": dist.version,
            "mappa_commit": commit, "policy": asdict(policy)}


def _unit(vector):
    length = np.linalg.norm(vector)
    return None if length < 1e-10 else vector / length


def _volume(xyz, atoms):
    a, b, c, d = xyz[list(atoms)]
    edges = [np.linalg.norm(xyz[i] - xyz[j]) for i, j in combinations(atoms, 2)]
    if min(edges) < 1e-10:
        return 0.0
    scale = math.exp(sum(math.log(v) for v in edges) / 6)
    return float(np.dot(np.cross(b - a, c - a), d - a) / scale**3)


def _orientation(xyz, center, neighbors):
    vectors = [_unit(xyz[j] - xyz[center]) for j in neighbors]
    if any(v is None for v in vectors):
        return 0.0
    return float(np.linalg.det(np.array(vectors)))


def _graphs(elements, xyz, wbo, policy):
    """Keep coordination contacts in AAM, but exclude weak nonbonded contacts
    from covalent stereocentre perception. No organic sanitisation of metals.
    """
    from ase.data import atomic_numbers, covalent_radii
    from mappa.frag import is_metal_element
    graph = nx.Graph()
    graph.add_nodes_from((i, {"element": e}) for i, e in enumerate(elements))
    covalent = graph.copy()
    for i, j in combinations(range(len(elements)), 2):
        if wbo[i, j] < policy.graph_floor:
            continue
        graph.add_edge(i, j)
        radius = covalent_radii[atomic_numbers[elements[i]]] + covalent_radii[atomic_numbers[elements[j]]]
        if wbo[i, j] >= policy.covalent_floor and np.linalg.norm(xyz[i] - xyz[j]) < 1.35 * radius:
            covalent.add_edge(i, j)
    return graph, covalent


def _colors(graph):
    colors = {i: graph.nodes[i]["element"] for i in graph}
    for _ in graph:
        keys = {i: (colors[i], tuple(sorted(colors[j] for j in graph[i]))) for i in graph}
        table = {key: j for j, key in enumerate(sorted(set(keys.values()), key=repr))}
        new = {i: table[key] for i, key in keys.items()}
        if len(set(new.values())) == len(set(colors.values())):
            return new
        colors = new
    return colors


def _side(graph, colors, center, excluded):
    side = sorted(set(graph[center]) - set(excluded), key=lambda i: (colors[i], i))
    if len(side) == 2 and colors[side[0]] != colors[side[1]]:
        return side[0]
    # The imine lone pair is an implicit second substituent.
    if len(side) == 1 and graph.nodes[center]["element"] in {"N", "P"}:
        return side[0]
    return None


def _axis_measure(xyz, atoms, axial, projection_tolerance=0.10):
    left, right, a, b = atoms
    axis = _unit(xyz[right] - xyz[left])
    if axis is None:
        return 0.0
    u, v = xyz[a] - xyz[left], xyz[b] - xyz[right]
    up, vp = u - np.dot(u, axis) * axis, v - np.dot(v, axis) * axis
    if (np.linalg.norm(up) <= projection_tolerance * np.linalg.norm(u)
            or np.linalg.norm(vp) <= projection_tolerance * np.linalg.norm(v)):
        return 0.0
    u, v = _unit(up), _unit(vp)
    if u is None or v is None:
        return 0.0
    return float(np.dot(np.cross(u, v), axis) if axial else np.dot(u, v))


def _site_vectors(xyz, center, sites):
    vectors = [_unit(np.mean(xyz[list(site)], axis=0) - xyz[center]) for site in sites]
    return None if any(v is None for v in vectors) else np.array(vectors)


def _angles(vectors):
    return np.degrees(np.arccos(np.clip(vectors @ vectors.T, -1, 1)))


def _coordination_angle_groups(covalent, center, sites):
    """Chemical site-pair classes for a coarse, label-invariant geometry gate.

    Equal site colors may permute. Distinguish bite angles within one connected
    ligand from angles between separate ligands, without rematching atoms or
    enumerating ligand permutations. Determine donor equivalence after removing
    the current coordination center, so threshold-dependent center--donor edges
    cannot make identical ligands appear different. Other atoms retain their
    chemical context; metal edges do not join separate ligands for bite angles.
    """
    from collections import defaultdict
    from mappa.frag import is_metal_element
    detached = covalent.subgraph(i for i in covalent if i != center).copy()
    colors = _colors(detached)
    ligand_graph = detached.subgraph(i for i in detached
        if not is_metal_element(detached.nodes[i]['element']))
    owner = {atom: number for number, part in enumerate(nx.connected_components(ligand_graph))
             for atom in part}
    labels = [tuple(sorted(colors[atom] for atom in site)) for site in sites]
    components = [{owner[a] for a in site if a in owner} for site in sites]
    groups = defaultdict(list)
    for a, b in combinations(range(len(sites)), 2):
        pair = tuple(sorted((labels[a], labels[b])))
        groups[pair, bool(components[a] & components[b])].append((a, b))
    return [groups[key] for key in sorted(groups)]


def _coordination_angle_deviations(reference, prediction, groups):
    """Compare unordered angles only inside the same chemical pair class."""
    deviations = []
    for pairs in groups:
        left = sorted(float(reference[a, b]) for a, b in pairs)
        right = sorted(float(prediction[a, b]) for a, b in pairs)
        deviations.extend(abs(a - b) for a, b in zip(left, right))
    return np.asarray(deviations)


def _coordination_frame(elements, xyz, wbo, covalent, center, policy):
    """Define reference sites and ligand topology from WBOs, without distance cuts.

    Pi-connected adjacent donors may form a haptic site. A metal--bridge or
    single P--N/P--C chelate bond must not merge separate donor positions.
    Equivalent terminal atoms on one ligand (e.g. the two O on SO2) form a
    local donor pool; this does not change the MAPPA atom correspondence.
    """
    from mappa.frag import is_metal_element

    metal = is_metal_element(elements[center])
    if not metal and elements[center] not in {"Si", "P", "S", "Se", "Te", "I", "Sb"}:
        return None
    neighbors = [i for i in range(len(elements)) if i != center
                 and wbo[center, i] >= policy.graph_floor]
    if len(neighbors) < 2:
        return None
    haptic = nx.Graph()
    haptic.add_nodes_from(neighbors)
    if metal:
        haptic.add_edges_from((i, j) for i, j in covalent.subgraph(neighbors).edges
                             if not is_metal_element(elements[i])
                             and not is_metal_element(elements[j])
                             and "H" not in (elements[i], elements[j])
                             and wbo[i, j] >= 1.1)
    sites = [tuple(sorted(part)) for part in nx.connected_components(haptic)]
    if len(sites) < 2:
        return None
    detached = covalent.subgraph(i for i in covalent if i != center)
    twins = {}
    for atom in detached:
        attached = tuple(sorted(detached[atom]))
        if len(attached) == 1 and not is_metal_element(elements[attached[0]]):
            twins.setdefault((elements[atom], attached), []).append(atom)
    pools = {i: (i,) for i in neighbors}
    occupied = set(neighbors)
    for atoms in twins.values():
        if len(occupied.intersection(atoms)) != 1:
            continue
        for i in occupied.intersection(atoms):
            # Two occupied equivalent atoms remain two required positions.
            pools[i] = tuple(j for j in atoms if j == i or j not in occupied)
    vectors = _site_vectors(xyz, center, sites)
    if vectors is None:
        raise ReferenceConstraintError(f"Collapsed reference coordination site at {center}")
    return {"kind": "coordination", "center": center, "sites": sites, "metal": metal,
            "donor_pools": pools,
            "angles": _angles(vectors),
            "angle_groups": _coordination_angle_groups(covalent, center, sites)}


def _check_coordination(frame, mapped, mapping, policy, prediction_topology, prediction_wbo):
    """Check the reference sites, without rebuilding a second hard-cutoff CN.

    Native MAPPA owns the bond-event verdict, including new bonds. This gate
    checks WBO retention of the reference sites and their angles. Distances
    are not acceptance predicates, including donor selection and equivalence.
    Only terminal graph twins within the same ligand can substitute for a
    donor here; no new molecular mapping or permutation search is performed.
    """
    center = frame["center"]
    centerP = mapping[center]
    vectors = []
    for site in frame["sites"]:
        selected = []
        supported = False
        for atom in site:
            candidates = frame["donor_pools"][atom]
            def contact(i):
                if prediction_wbo is not None:
                    order = float(prediction_wbo[centerP, mapping[i]])
                    bonded = order >= policy.coordination_retention_floor
                elif prediction_topology is not None:
                    bonded = prediction_topology[0].has_edge(centerP, mapping[i])
                    order = float(bonded)
                else:
                    bonded, order = True, 0.0
                # Prefer the mapped reference donor on an exact WBO tie.
                # Neither distances nor angles select a different donor.
                return bonded, order, i == atom
            chosen = max(candidates, key=contact)
            selected.append(chosen)
            supported |= contact(chosen)[0]
        if not supported:
            return {"reason": "coordination_site_lost", "site": list(site),
                    "donor_candidates": sorted({i for atom in site for i in frame["donor_pools"][atom]}),
                    "retention_WBO_floor": policy.coordination_retention_floor}
        vector = _unit(mapped[selected].mean(axis=0) - mapped[center])
        if vector is None:
            return {"reason": "collapsed_coordination_site", "site": list(site)}
        vectors.append(vector)
    values = _coordination_angle_deviations(frame["angles"], _angles(np.array(vectors)),
                                            frame["angle_groups"])
    rms, maximum = float(np.sqrt(np.mean(values**2))), float(np.max(values))
    if rms > policy.coordination_angle_rms_deg or maximum > policy.coordination_angle_max_deg:
        return {"reason": "coordination_angles", "rms_deg": rms, "max_deg": maximum,
                "comparison": "reference_chemical_site_pair_angle_profiles"}
    return None


def reference_constraints(elements, xyz, wbo, policy=VerificationPolicy(), annotations=None):
    """Perceive tetrahedral, pyramidal, E/Z, cumulene and coordination frames.

    Atropisomeric single bonds require ``axial_bonds: [[a,b], ...]``. A single
    conformer cannot establish a rotational barrier; ordinary biphenyl torsion
    is deliberately not frozen. ``axial_frames: [[a,b,left,right], ...]`` can
    name other explicitly specified axes. ``double_bonds`` adds curated E/Z
    bonds when the continuous WBO does not exceed the automatic threshold.
    """
    from mappa.frag import is_metal_element
    annotations = annotations or {}
    if not isinstance(annotations, dict):
        raise ReferenceConstraintError("Stereo annotations must be an object")
    allowed = {"axial_bonds", "axial_frames", "double_bonds"}
    if set(annotations) - allowed:
        raise ReferenceConstraintError(f"Unknown stereo annotations: {sorted(set(annotations) - allowed)}")
    graph, covalent = _graphs(elements, xyz, wbo, policy)
    colors = _colors(covalent)
    constraints, skipped = [], []
    for center in covalent:
        if is_metal_element(elements[center]):
            continue
        neighbors = sorted(covalent[center], key=lambda j: (colors[j], j))
        if len(neighbors) == 4 and len({colors[j] for j in neighbors}) == 4:
            measure = _volume(xyz, neighbors)
            if abs(measure) > policy.volume_tolerance:
                constraints.append({"kind": "tetrahedral", "center": center,
                                    "atoms": neighbors, "reference": measure})
            else:
                skipped.append({"kind": "tetrahedral", "center": center, "reason": "reference_planar"})
        elif (elements[center] in {"P", "As", "S", "Se"} and len(neighbors) == 3
              and len({colors[j] for j in neighbors}) == 3):
            measure = _orientation(xyz, center, neighbors)
            if abs(measure) > policy.volume_tolerance:
                constraints.append({"kind": "pyramidal", "center": center,
                                    "atoms": neighbors, "reference": measure})

    explicit_double = {tuple(sorted(_indices(pair, len(elements), 2)))
                       for pair in annotations.get("double_bonds", [])}
    doubles = nx.Graph()
    for i, j in covalent.edges:
        if wbo[i, j] < policy.double_bond_floor and (min(i, j), max(i, j)) not in explicit_double:
            continue
        # Aromatic and small-ring bonds are not free E/Z stereobonds.
        reduced = covalent.copy()
        reduced.remove_edge(i, j)
        try:
            ring_size = nx.shortest_path_length(reduced, i, j) + 1
        except nx.NetworkXNoPath:
            ring_size = math.inf
        if ring_size <= 7 and (min(i, j), max(i, j)) not in explicit_double:
            continue
        doubles.add_edge(i, j)
    if any(not covalent.has_edge(*pair) for pair in explicit_double):
        raise ReferenceConstraintError("An annotated double bond is absent from the covalent graph")
    for component in nx.connected_components(doubles):
        path_graph = doubles.subgraph(component)
        ends = sorted(i for i in component if path_graph.degree[i] == 1)
        if len(ends) != 2 or any(path_graph.degree[i] > 2 for i in component):
            continue
        left, right = ends
        path = nx.shortest_path(path_graph, left, right)
        # Internal cumulene atoms have no additional substituents.
        if any(covalent.degree[i] != 2 for i in path[1:-1]):
            continue
        a = _side(covalent, colors, left, component)
        b = _side(covalent, colors, right, component)
        if a is None or b is None:
            continue
        axial = len(path) % 2 == 1  # even number of cumulated double bonds
        atoms = [left, right, a, b]
        measure = _axis_measure(xyz, atoms, axial, policy.projection_tolerance)
        kind = "axial_cumulene" if axial else "double_bond"
        if abs(measure) <= policy.projection_tolerance:
            if any(tuple(sorted(pair)) in explicit_double for pair in zip(path, path[1:])):
                raise ReferenceConstraintError(f"Undefined annotated E/Z geometry: {path}")
            skipped.append({"kind": kind, "atoms": atoms, "reason": "reference_degenerate"})
            continue
        constraints.append({"kind": kind, "atoms": atoms, "reference": measure})

    explicit_frames = [_indices(frame, len(elements), 4) for frame in annotations.get("axial_frames", [])]
    for pair in annotations.get("axial_bonds", []):
        left, right = _indices(pair, len(elements), 2)
        if not covalent.has_edge(left, right):
            raise ReferenceConstraintError(f"Annotated axis is not a covalent bond: {pair}")
        a, b = _side(covalent, colors, left, [right]), _side(covalent, colors, right, [left])
        if a is None or b is None:
            raise ReferenceConstraintError(f"Axis has indistinguishable/undefined substituents: {pair}")
        explicit_frames.append([left, right, a, b])
    for atoms in explicit_frames:
        if atoms[2] not in covalent[atoms[0]] or atoms[3] not in covalent[atoms[1]]:
            raise ReferenceConstraintError(f"Axial frame substituents must be bonded to their endpoints: {atoms}")
        measure = _axis_measure(xyz, atoms, True, policy.projection_tolerance)
        if abs(measure) <= policy.projection_tolerance:
            raise ReferenceConstraintError(f"Annotated axis is planar/degenerate: {atoms}")
        constraints.append({"kind": "axial_bond", "atoms": atoms, "reference": measure})

    # Coordination ligand identity uses WBO-only topology. Keep the existing
    # distance-filtered covalent graph above exclusively for nonmetal stereo.
    coordination_covalent = graph.copy()
    coordination_covalent.remove_edges_from(
        (i, j) for i, j in graph.edges if wbo[i, j] < policy.covalent_floor)
    for center in graph:
        frame = _coordination_frame(elements, xyz, wbo, coordination_covalent, center, policy)
        if frame is not None:
            constraints.append(frame)
    return graph, constraints, skipped


def _indices(values, count, length):
    if (len(values) != length or any(type(i) is not int or not 0 <= i < count for i in values)
            or len(set(values)) != length):
        raise ReferenceConstraintError(f"Expected {length} distinct zero-based reference atom indices: {values}")
    return list(values)


def check_mapping(constraints, xyzP, mapping, policy=VerificationPolicy(), prediction_topology=None,
                  prediction_wbo=None):
    """Check fixed-map stereo and coarse ligand geometry, including collapse."""
    failures = []
    counts = {kind: 0 for kind in ("tetrahedral", "pyramidal", "double_bond", "axial_cumulene", "axial_bond", "coordination")}
    mapped = np.array([xyzP[mapping[i]] for i in range(len(mapping))])
    for constraint in constraints:
        kind = constraint["kind"]
        counts[kind] += 1
        if kind == "coordination":
            issue = _check_coordination(constraint, mapped, mapping, policy,
                                        prediction_topology, prediction_wbo)
            if issue:
                failures.append({"kind": kind, "center": constraint["center"], **issue})
            continue
        if kind == "tetrahedral":
            value, tolerance = _volume(mapped, constraint["atoms"]), policy.volume_tolerance
        elif kind == "pyramidal":
            value, tolerance = _orientation(mapped, constraint["center"], constraint["atoms"]), policy.volume_tolerance
        else:
            value = _axis_measure(mapped, constraint["atoms"], kind.startswith("axial"), policy.projection_tolerance)
            tolerance = policy.projection_tolerance
        if abs(value) <= tolerance or value * constraint["reference"] < 0:
            failures.append({"kind": kind, "atoms": constraint["atoms"],
                             "reason": "configuration_lost" if abs(value) <= tolerance else "configuration_inverted",
                             "reference": constraint["reference"], "prediction": value})
    return {"counts": counts, "failures": failures,
            "stereo_pass": not any(f["kind"] != "coordination" for f in failures),
            "geometry_pass": not any(f["kind"] == "coordination" for f in failures)}


def _bond_changes(mapping, wboR, wboP, elements, policy):
    from mappa.frag import classify_bonds
    if set(mapping) != set(range(len(elements))) or set(mapping.values()) != set(range(len(elements))):
        raise VerificationUnresolved("MAPPA returned an incomplete atom mapping")
    broken, formed, _, _ = classify_bonds(
        mapping, wboR, wboP, dwbo_threshold=policy.bond_change,
        elements_R=elements, elements_P=[elements[i] for i in sorted(mapping, key=mapping.get)],
        metal_dwbo_threshold=policy.metal_bond_change)
    return len(broken), len(formed)


def _mappa_one_mapping(problem, policy, info):
    """Call current upstream MAPPA and take its first zero-event candidate."""
    from mappa import AAMSearchConfig, search_aam
    from mappa.postprocessing import decode_events, EventDecodeConfig
    from mappa.final_branches import FinalBranchCatalogue

    config = AAMSearchConfig(graph_floor=policy.graph_floor, cut_floor=policy.graph_floor,
        iso_tolerance=1.0, event_threshold=policy.bond_change,
        metal_event_threshold=policy.metal_bond_change, seed_count=policy.seed_count,
        branch_limit=policy.branch_limit, sweep_cuts=False)
    def decode(source):
        catalogue = source
        if not isinstance(source, FinalBranchCatalogue):
            catalogue = FinalBranchCatalogue(problem)
            catalogue.add_aam(source)
        info['families'] += len(catalogue.families)
        info['incomplete_paths'] += catalogue.incomplete_paths
        # A raw native representative is already a complete mapping.
        # Check MAPPA bond events, then stop: unused families need no
        # event enumeration or global completeness proof for this decision.
        for family in catalogue.families:
            mapping = dict(family.mapping)
            if _bond_changes(mapping, problem.reactant.wbo, problem.product.wbo,
                             problem.reactant.elements, policy) != (0, 0):
                continue
            info['event_class_id'] = 'direct_native_zero_event_witness'
            info['supporting_families'] = 1
            info['decode_complete'] = False
            info['event_decoding_status'] = 'unneeded_after_native_zero_event_mapping'
            info['mapping_source'] = 'native_family_representative'
            return mapping
        # The upstream API requires a finite per-family soft time. Using the
        # full case budget cannot stop a family before the external case guard.
        seconds = info['wall_time_seconds']
        decoded = decode_events(catalogue, EventDecodeConfig(threshold=policy.bond_change,
            metal_threshold=policy.metal_bond_change, max_events=0, seconds_per_family=seconds))
        info['families_decoded'] += len(decoded.family_reports)
        window_complete = all(r['complete'] for r in decoded.family_reports)
        info['decode_complete'] &= window_complete
        info['decode_unresolved_reasons'].extend(
            r['reason'] for r in decoded.family_reports if not r['complete'])
        info['event_decoding_status'] = 'complete' if window_complete else 'incomplete'
        if not decoded.candidates:
            return None
        candidate = decoded.candidates[0]
        if candidate.total != 0:
            raise RuntimeError('MAPPA zero-event decoder emitted a nonzero-event candidate')
        info['event_class_id'] = candidate.id
        info['supporting_families'] = len(candidate.family_ids)
        info['mapping_source'] = 'native_zero_event_decoder'
        return dict(candidate.mapping)

    info['cut_sweep_enabled'] = False
    aam = search_aam(problem, config, workers=1)
    info['attempts'].append({'sweep_cuts': False, 'capped': bool(aam.graph.capped)})
    return decode(aam)


def verify_arrays(elementsR, xyzR, wboR, elementsP, xyzP, wboP, *,
                  policy=VerificationPolicy(), annotations=None, wall_time_seconds=300.):
    """MAPPA connectivity, then one coordinate check on its unchanged mapping.

    The caller enforces the whole-case wall time. MolDraft neither searches for
    alternative correspondences nor re-proves membership in native families.
    A negative coordinate result describes this one selected correspondence.
    """
    from collections import Counter
    from mappa import AAMProblem, MolecularEndpoint
    if not math.isfinite(wall_time_seconds) or wall_time_seconds <= 0:
        raise ValueError('wall_time_seconds must be finite and positive')
    record = {'verification': provenance(policy), 'aam_pass': False,
              'stereo_pass': None, 'geometry_pass': None, 'overall_pass': False}
    xyzR, xyzP, wboR, wboP = map(lambda x: np.asarray(x, dtype=float), (xyzR, xyzP, wboR, wboP))
    for elements, xyz, wbo in ((elementsR, xyzR, wboR), (elementsP, xyzP, wboP)):
        n = len(elements)
        if xyz.shape != (n, 3) or wbo.shape != (n, n) or not np.isfinite(xyz).all() or not np.isfinite(wbo).all():
            raise ValueError('Expected finite (N,3) coordinates and (N,N) WBO matrices')
    if Counter(elementsR) != Counter(elementsP):
        return {**record, 'flag': 'wrong_mol', 'error': 'element composition differs'}
    info = dict(mode='upstream_single_mapping', attempts=[], event_window=0,
                event_threshold=policy.bond_change, metal_event_threshold=policy.metal_bond_change,
                families=0, families_decoded=0, incomplete_paths=0, decode_complete=True,
                decode_unresolved_reasons=[], upstream_coordinate_selection=False,
                mapping_selection='first_upstream_zero_event_candidate',
                wall_time_seconds=wall_time_seconds, timeout_authority='caller_whole_case_watchdog',
                mapping_changed_by_stereo=False, coordinate_checks=0,
                stereo_decision_scope='single_MAPPA_correspondence',
                coordination_decision_scope='reference_sites_WBO_retention_and_chemical_angle_profiles')
    record['mappa'] = info
    started = time.monotonic()
    try:
        problem = AAMProblem(MolecularEndpoint(elementsR, xyzR, wboR),
                             MolecularEndpoint(elementsP, xyzP, wboP), name='verification')
        mapping = _mappa_one_mapping(problem, policy, info)
        if mapping is None:
            info['failure_stage'] = 'connectivity'
            if not info['decode_complete']:
                raise VerificationUnresolved('MAPPA zero-event decoding did not finish; no connectivity verdict')
            if any(attempt['capped'] for attempt in info['attempts']) or info['incomplete_paths']:
                info['connectivity_failure_reason'] = 'incomplete_search_without_zero_event_mapping'
                raise VerificationUnresolved(
                    'MAPPA search was truncated or retained incomplete paths without a zero-event mapping; '
                    'no connectivity verdict')
            info['connectivity_decision_scope'] = 'configured_MAPPA_search_result'
            info['connectivity_failure_reason'] = (
                'no_zero_event_mapping_in_retained_families' if info['families']
                else 'no_complete_mapping_returned')
            return {**record, 'flag': 'wrong_mol', 'n_broken': None, 'n_formed': None,
                    'error': 'Configured MAPPA search returned no complete zero-event mapping'}
        broken, formed = _bond_changes(mapping, wboR, wboP, elementsR, policy)
        if broken or formed:
            info['failure_stage'] = 'connectivity'
            info['connectivity_failure_reason'] = 'nonzero_bond_events_on_selected_mapping'
            return {**record, 'flag': 'wrong_mol', 'n_broken': broken, 'n_formed': formed,
                    'mapping': [mapping[i] for i in range(len(mapping))],
                    'error': 'Selected complete mapping has nonzero WBO bond events'}
        record.update(aam_pass=True, n_broken=0, n_formed=0)
        _, constraints, skipped = reference_constraints(elementsR, xyzR, wboR, policy, annotations)
        topology = _graphs(elementsP, xyzP, wboP, policy)
        checked = check_mapping(constraints, xyzP, mapping, policy, topology, wboP)
        info['coordinate_checks'] = 1
        return _finish(record, checked, mapping, skipped)
    except VerificationUnresolved as exc:
        exc.verification_record = record
        raise
    finally:
        info['seconds'] = round(time.monotonic() - started, 6)


def _finish(record, checked, mapping, skipped):
    record.update(checked)
    record.update(mapping=[mapping[i] for i in range(len(mapping))],
                  reference_skipped=skipped, mappings_checked=1,
                  stereo_centres=checked["counts"]["tetrahedral"] + checked["counts"]["pyramidal"],
                  stereo_inverted=sum(f["reason"] == "configuration_inverted" and f["kind"] in {"tetrahedral", "pyramidal"}
                                      for f in checked["failures"]),
                  stereo_inverted_total=sum(f["reason"] == "configuration_inverted" for f in checked["failures"]),
                  stereo_lost=sum(f["reason"] == "configuration_lost" for f in checked["failures"]))
    record["overall_pass"] = checked["stereo_pass"] and checked["geometry_pass"]
    record["flag"] = "ok" if record["overall_pass"] else "wrong_stereo" if not checked["stereo_pass"] else "wrong_geometry"
    return record
