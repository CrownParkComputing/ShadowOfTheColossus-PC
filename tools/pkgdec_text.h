// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
// sotc: the little of the ports' setup/setup.h that pkgdec.cpp uses, inlined so the pkgdec tool
// builds alone. Linux paths are UTF-8 bytes, so these conversions do not depend on the locale.

#include <filesystem>
#include <string>
#include <string_view>

namespace setup {

// Why the decryption stopped; the text is meant for the user.
struct Error {
    std::wstring message;
};

inline std::wstring widen(std::string_view s) {
    std::wstring out;
    for (size_t i = 0; i < s.size();) {
        const unsigned char c = s[i];
        unsigned long cp; size_t extra;
        if (c < 0x80) { cp = c; extra = 0; }
        else if ((c & 0xe0) == 0xc0) { cp = c & 0x1f; extra = 1; }
        else if ((c & 0xf0) == 0xe0) { cp = c & 0x0f; extra = 2; }
        else if ((c & 0xf8) == 0xf0) { cp = c & 0x07; extra = 3; }
        else { out += L'?'; ++i; continue; }
        if (i + extra >= s.size()) { out += L'?'; break; }
        for (size_t j = 1; j <= extra; ++j) {
            if ((s[i + j] & 0xc0) != 0x80) { cp = '?'; extra = 0; break; }
            cp = cp << 6 | (s[i + j] & 0x3f);
        }
        out += static_cast<wchar_t>(cp);
        i += extra + 1;
    }
    return out;
}

inline std::string narrow(std::wstring_view s) {
    std::string out;
    for (wchar_t w : s) {
        const unsigned long cp = static_cast<unsigned long>(w);
        if (cp < 0x80) out += static_cast<char>(cp);
        else if (cp < 0x800) {
            out += static_cast<char>(0xc0 | (cp >> 6));
            out += static_cast<char>(0x80 | (cp & 0x3f));
        } else {
            out += static_cast<char>(0xe0 | (cp >> 12));
            out += static_cast<char>(0x80 | ((cp >> 6) & 0x3f));
            out += static_cast<char>(0x80 | (cp & 0x3f));
        }
    }
    return out;
}

// A path as text for the user, and text back as a path.
inline std::wstring text(const std::filesystem::path& p) {
    return widen(p.generic_u8string());
}
inline std::filesystem::path path_of(const std::wstring& s) {
    return std::filesystem::u8path(narrow(s));
}

} // namespace setup
