// SPDX-License-Identifier: GPL-2.0-or-later
// sotc-pkgdec: the pkgdec tool of scripts/pkg_extract.py, without the ports' setup program around
// it. The extractor calls it as
//
//     sotc-pkgdec --pkg-decrypt <pkg> <offset> <length> <out> <data-key-hex> <tweak-key-hex>
//                 <first-encrypted-sector>
//
// and the bulk of a .pkg's game data comes out of it in seconds.

#include "pkgdec.h"
#include "pkgdec_text.h"

#include <vector>

int main(int argc, char** argv) {
    int skip = 1;
    if (argc > 1 && std::string_view(argv[1]) == "--pkg-decrypt") {
        ++skip; // the mode flag itself, as the ports' setup main consumes it
    }
    std::vector<std::wstring> args;
    args.reserve(argc > skip ? argc - skip : 0);
    for (int i = skip; i < argc; ++i) args.push_back(setup::widen(argv[i]));
    return setup::pkg_decrypt_main(args);
}
