{pkgs}: {
  deps = [
    pkgs.postgresql
    pkgs.rustc
    pkgs.pkg-config
    pkgs.openssl
    pkgs.libiconv
    pkgs.cargo
    pkgs.zlib
    pkgs.tk
    pkgs.tcl
    pkgs.openjpeg
    pkgs.libxcrypt
    pkgs.libwebp
    pkgs.libtiff
    pkgs.libjpeg
    pkgs.libimagequant
    pkgs.lcms2
    pkgs.freetype
  ];
}
