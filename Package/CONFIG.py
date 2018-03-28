import ops
import iopc

TARBALL_FILE="gdk-pixbuf-2.36.11.tar.xz"
TARBALL_DIR="gdk-pixbuf-2.36.11"
INSTALL_DIR="gdk-pixbuf-bin"
pkg_path = ""
output_dir = ""
tarball_pkg = ""
tarball_dir = ""
install_dir = ""
install_tmp_dir = ""
cc_host = ""
dst_include_dir = ""
dst_lib_dir = ""

def set_global(args):
    global pkg_path
    global output_dir
    global tarball_pkg
    global install_dir
    global install_tmp_dir
    global tarball_dir
    global cc_host
    global dst_include_dir
    global dst_lib_dir
    pkg_path = args["pkg_path"]
    output_dir = args["output_path"]
    tarball_pkg = ops.path_join(pkg_path, TARBALL_FILE)
    install_dir = ops.path_join(output_dir, INSTALL_DIR)
    install_tmp_dir = ops.path_join(output_dir, INSTALL_DIR + "-tmp")
    tarball_dir = ops.path_join(output_dir, TARBALL_DIR)
    cc_host_str = ops.getEnv("CROSS_COMPILE")
    cc_host = cc_host_str[:len(cc_host_str) - 1]
    dst_include_dir = ops.path_join("include",args["pkg_name"])
    dst_lib_dir = ops.path_join(install_dir, "lib")

def MAIN_ENV(args):
    set_global(args)

    ops.exportEnv(ops.setEnv("CC", ops.getEnv("CROSS_COMPILE") + "gcc"))
    ops.exportEnv(ops.setEnv("CXX", ops.getEnv("CROSS_COMPILE") + "g++"))
    ops.exportEnv(ops.setEnv("CROSS", ops.getEnv("CROSS_COMPILE")))
    ops.exportEnv(ops.setEnv("DESTDIR", install_tmp_dir))

    cc_sysroot = ops.getEnv("CC_SYSROOT")

    cflags = ""
    cflags += " -I" + ops.path_join(cc_sysroot, 'usr/include')
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include')
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/libtiff')

    ldflags = ""
    ldflags += " -L" + ops.path_join(cc_sysroot, 'lib')
    ldflags += " -L" + ops.path_join(cc_sysroot, 'usr/lib')
    ldflags += " -L" + ops.path_join(iopc.getSdkPath(), 'lib')
    ldflags += " -L" + ops.path_join(iopc.getSdkPath(), 'usr/lib')
    ldflags += " -lz -lpcre -lffi -ltiff"

    ops.exportEnv(ops.setEnv("LDFLAGS", ldflags))
    ops.exportEnv(ops.setEnv("CFLAGS", cflags))

    base_dep_cflags = ""
    base_dep_cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/libglib')
    base_dep_cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/libtiff')

    base_dep_libs = ""
    base_dep_libs += " -L" + ops.path_join(iopc.getSdkPath(), 'lib') + " -lpcre"
    base_dep_libs += " -L" + ops.path_join(iopc.getSdkPath(), 'ur/lib') + " -lffi"
    ops.exportEnv(ops.setEnv("BASE_DEPENDENCIES_CFLAGS", base_dep_cflags))
    ops.exportEnv(ops.setEnv("BASE_DEPENDENCIES_LIBS", base_dep_libs))

    glib_cflags = ""
    glib_cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include')
    glib_cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/libglib')
    glib_cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/libtiff')
    glib_cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/libglib/glib-2.0')
    glib_cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/libglib/gio-unix-2.0')

    glib_libs = ""
    glib_libs += " -L" + ops.path_join(iopc.getSdkPath(), 'lib')
    glib_libs += " -L" + ops.path_join(iopc.getSdkPath(), 'ur/lib')
    glib_libs += " -lgio-2.0 -lglib-2.0 -lgmodule-2.0 -lgobject-2.0 -lgthread-2.0 -lffi -lpcre -lz"

    ops.exportEnv(ops.setEnv("GLIB_CFLAGS", glib_cflags))
    ops.exportEnv(ops.setEnv("GLIB_LIBS", glib_libs))

    ops.exportEnv(ops.setEnv("PKG_CONFIG_LIBDIR", ops.path_join(iopc.getSdkPath(), "pkgconfig")))
    ops.exportEnv(ops.setEnv("PKG_CONFIG_SYSROOT_DIR", iopc.getSdkPath()))
    #ops.exportEnv(ops.setEnv("LIBS", libs))
    #extra_conf.append('CFLAGS="-I' + ops.path_join(iopc.getSdkPath(), 'usr/include/libz') + '"')

    return False

def MAIN_EXTRACT(args):
    set_global(args)

    ops.unTarXz(tarball_pkg, output_dir)
    #ops.copyto(ops.path_join(pkg_path, "finit.conf"), output_dir)

    return True

def MAIN_PATCH(args, patch_group_name):
    set_global(args)
    for patch in iopc.get_patch_list(pkg_path, patch_group_name):
        if iopc.apply_patch(tarball_dir, patch):
            continue
        else:
            sys.exit(1)

    return True

def MAIN_CONFIGURE(args):
    set_global(args)

    print "SDK include path:" + iopc.getSdkPath()

    extra_conf = []
    extra_conf.append("--without-x11")
    extra_conf.append("--without-gdiplus")
    extra_conf.append("--disable-gtk-doc-html")
    #extra_conf.append("--disable-glibtest")
    extra_conf.append("--without-libtiff")
    extra_conf.append("--without-libjpeg")
    extra_conf.append("--without-libpng")
    extra_conf.append("--host=" + cc_host)
    extra_conf.append("gt_cv_func_CFLocaleCopyCurrent=no")
    extra_conf.append("gt_cv_func_CFPreferencesCopyAppValue=no")
    print extra_conf
    iopc.configure(tarball_dir, extra_conf)

    return True

def MAIN_BUILD(args):
    set_global(args)

    ops.mkdir(install_dir)
    ops.mkdir(install_tmp_dir)
    iopc.make(tarball_dir)
    iopc.make_install(tarball_dir)
    return False

def MAIN_INSTALL(args):
    set_global(args)

    ops.mkdir(install_dir)

    ops.mkdir(dst_lib_dir)

    libcairo = "libcairo.so.2.11400.12"
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/lib/" + libcairo), dst_lib_dir)
    ops.ln(dst_lib_dir, libcairo, "libcairo.so.2")
    ops.ln(dst_lib_dir, libcairo, "libcairo.so")

    ops.mkdir(dst_include_dir)
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/include/cairo/cairo-deprecated.h"), dst_include_dir)
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/include/cairo/cairo-features.h"), dst_include_dir)
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/include/cairo/cairo.h"), dst_include_dir)
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/include/cairo/cairo-script.h"), dst_include_dir)
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/include/cairo/cairo-version.h"), dst_include_dir)

    iopc.installBin(args["pkg_name"], ops.path_join(ops.path_join(install_dir, "lib"), "."), "lib")
    iopc.installBin(args["pkg_name"], dst_include_dir, "include")

    return False

def MAIN_CLEAN_BUILD(args):
    set_global(args)

    return False

def MAIN(args):
    set_global(args)

