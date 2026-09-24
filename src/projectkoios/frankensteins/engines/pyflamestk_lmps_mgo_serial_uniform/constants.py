SOURCE_COMPONENT = "pyflamestk"
SOURCE_REPOSITORY_URL = "https://github.com/eragasa/pyflamestk"
SOURCE_REVISION = "5b8368cc88d91bc56f9cc1c8a7fa8d9ea3d6b359"
SOURCE_TREE = "02e20f61a9b554ed0dcbda15bb24adc21e942007"
SOURCE_LICENSE_PATH = "LICENSE"
SOURCE_LICENSE_SHA256 = (
    "8e8ff7b5f5de2f4f1b48a18108d6268769739d622cfb671078565ab56bef28aa"
)
EXAMPLE_ROOT = "examples/lmps_MgO_serial_uniform"
ENGINE_NAME = "pyflamestk-lmps-mgo-serial-uniform"

SOURCE_FILES: dict[str, tuple[str, int]] = {
    "examples/lmps_MgO_serial_uniform/README": (
        "5b70b0101b3613c4c292485b3a54f6cd9b1094df6a72f12b92a4a9d21e542a8a",
        177,
    ),
    "examples/lmps_MgO_serial_uniform/buckingham_uniform.py": (
        "a3db198324c82d19adc96aca7c896f7fd295ebfbbb629a43fb84c40c583e7914",
        1069,
    ),
    "examples/lmps_MgO_serial_uniform/cleanup.sh": (
        "1824b1d761e1f18b1df54d59b2e0dfa513815b2b7b4ffa618393d54880e90138",
        60,
    ),
    "examples/lmps_MgO_serial_uniform/lmp_scripts_db/E_min_all/in.min": (
        "d5415eefdec0727c52a08b9050726b74682cea761b0a926e1a8c83045bd5ca70",
        1599,
    ),
    "examples/lmps_MgO_serial_uniform/lmp_scripts_db/E_min_all/runsimulation.sh": (
        "416b3cf9268cfeb8b6996abd13da41df57e70dab2c12d085220d61948c14969e",
        300,
    ),
    "examples/lmps_MgO_serial_uniform/lmp_scripts_db/E_min_pos/in.min_pos": (
        "5d7f8c20b8035668218e4638fa2f735530e447af76a9645adda90965835b81d2",
        1540,
    ),
    "examples/lmps_MgO_serial_uniform/lmp_scripts_db/E_min_pos/runsimulation.sh": (
        "6096a39c2943b089a1a72be699b5cf90d420fa6a2d43568e566d1293cd47271f",
        266,
    ),
    "examples/lmps_MgO_serial_uniform/lmp_scripts_db/elastic/calc_fcc.in": (
        "29fa4751878ee7b0111360108029a86273b4c5f57a520c377d2f23db11c1dbae",
        1288,
    ),
    "examples/lmps_MgO_serial_uniform/lmp_scripts_db/elastic/displace.mod": (
        "23cc06b4a323ba6ab742e659c1c7859de2082514a78b628775be3866076b79f4",
        3446,
    ),
    "examples/lmps_MgO_serial_uniform/lmp_scripts_db/elastic/displace_restart.mod": (
        "a8bc57d8b012963e0c9aa9de0385063eb3074579e097cafcb3c0523ceffcf9a8",
        3434,
    ),
    "examples/lmps_MgO_serial_uniform/lmp_scripts_db/elastic/displace_reverse.mod": (
        "688f92385a4b7a8d9c85fcabaee143ef97e36db82ab55401e02cbf63eff2539e",
        4469,
    ),
    "examples/lmps_MgO_serial_uniform/lmp_scripts_db/elastic/in.elastic": (
        "38ccc961d5af5f8703299fc3b5ef30fd72614bb992b45c30a03adb45d1578bb4",
        5348,
    ),
    "examples/lmps_MgO_serial_uniform/lmp_scripts_db/elastic/init.mod": (
        "328e6d75d13a3afc7f2d7c2d0c7f622f4c6bbcace57fdb1571f10db0da99ce10",
        405,
    ),
    "examples/lmps_MgO_serial_uniform/lmp_scripts_db/elastic/lammps.structure": (
        "9652709423cee65583d4792a170bf322fd04b863987f8029e7c3a9d0d66cb3e4",
        10051,
    ),
    "examples/lmps_MgO_serial_uniform/lmp_scripts_db/elastic/potential.mod": (
        "a36c301162713cc4738f1f8ad72752216237827049a9ac35802c35b86a92cfb5",
        312,
    ),
    "examples/lmps_MgO_serial_uniform/lmp_scripts_db/elastic/runsimulation.sh": (
        "43a8a1420254275efa41f7c41afb0ef1993de9ee6aa6dc2fa151919b3faede1a",
        268,
    ),
    "examples/lmps_MgO_serial_uniform/lmp_scripts_db/single_point/in.single_point": (
        "48012b0eb57ee17eeea44c35250917bfa53a208dd885ea2a60b3b809fa5ea402",
        1501,
    ),
    "examples/lmps_MgO_serial_uniform/lmp_scripts_db/single_point/potential.mod": (
        "8df212104e12dd461fa635ddc633dc09fe90a7d3257b1ec71eff85a3f6d5b492",
        1255,
    ),
    "examples/lmps_MgO_serial_uniform/lmp_scripts_db/single_point/runsimulation.sh": (
        "088cc0c610542dea3c004aa484e4a220b27c80954ce9b8762aaf040c061b4699",
        271,
    ),
    "examples/lmps_MgO_serial_uniform/pyposmat.config": (
        "6be0448baabe765d39ee7ae12ac88368f613baf1cf23aed29e426081cbac36ac",
        1424,
    ),
    "examples/lmps_MgO_serial_uniform/pyposmat.potential": (
        "bb6bb6461468c96012acfa298bd1fc473d771d3ce82f1c4effed662e9ffa1e1d",
        767,
    ),
    "examples/lmps_MgO_serial_uniform/pyposmat.qoi": (
        "038bb53335c73f4408b9ab3bcd1e7c7333861c4fdbcd0e7311827eb9f2c6b6d6",
        1472,
    ),
    "examples/lmps_MgO_serial_uniform/structure_db/MgO_NaCl_001_s.vasp": (
        "62ae8aac41638df7723df8f36b99f7d256d3289bd5acd1caa3f4a54eab41396d",
        1502,
    ),
    "examples/lmps_MgO_serial_uniform/structure_db/MgO_NaCl_111.vasp": (
        "3780d46aa8911640b8a1f45eb5b9c86a635249baec0adeac98936f96386cfc1a",
        444,
    ),
    "examples/lmps_MgO_serial_uniform/structure_db/MgO_NaCl_333.vasp": (
        "98341533afe24078e68f6e243e51d28c45282e4d2c22c1f97e218ab2e7e6ed3d",
        7312,
    ),
    "examples/lmps_MgO_serial_uniform/structure_db/MgO_NaCl_333_fr_a.vasp": (
        "09647488d35aaab6b78c03ad404d6b3ff78719c26eab2c99c04dd9e21802d8b9",
        7312,
    ),
    "examples/lmps_MgO_serial_uniform/structure_db/MgO_NaCl_333_fr_c.vasp": (
        "a4d27e7024f6288ecdb5321527612128760ea4b653664862ef0112df0afac5db",
        7312,
    ),
    "examples/lmps_MgO_serial_uniform/structure_db/MgO_NaCl_333_sch.vasp": (
        "6b9ec0044126ff3df79c6a64604d3c32f32859ba926f1a63bc538b8b0e61f0ac",
        7246,
    ),
    "examples/lmps_MgO_serial_uniform/structure_db/MgO_NaCl_unit.vasp": (
        "9558dbbce6736a7f9369bfeeb14d1d4a1c9f109b02e8c576bf6129134f02132f",
        349,
    ),
    "pyflamestk/lammps.py": (
        "17eea5261f363e8b4f097909a94153d5a7a5f8628afc0ebb4108120a09255986",
        41267,
    ),
    "pyflamestk/pyposmat.py": (
        "3855a60ea811a4343ef05fd3381bf27ef6a98f65e14a5fc78d0340a7ef8c00bd",
        73199,
    ),
    "pyflamestk/qoi.py": (
        "4e35630253695eb4cef3943876788ef6de493fbdf421862a14291429c31bb051",
        11626,
    ),
}

__all__ = [
    "ENGINE_NAME",
    "EXAMPLE_ROOT",
    "SOURCE_COMPONENT",
    "SOURCE_FILES",
    "SOURCE_LICENSE_PATH",
    "SOURCE_LICENSE_SHA256",
    "SOURCE_REPOSITORY_URL",
    "SOURCE_REVISION",
    "SOURCE_TREE",
]
