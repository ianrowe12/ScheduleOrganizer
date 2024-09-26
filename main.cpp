#include <pybind11/embed.h>
#include "mainwindow.h"
#include <iostream>
#include <QApplication>

namespace py = pybind11;

int main(int argc, char *argv[])
{
    py::scoped_interpreter guard{};  // Start the Python interpreter

    py::module sys = py::module_::import("sys");
    sys.attr("executable") = "/Users/ianrowe/.pyenv/versions/3.12.0/bin/python3";  // Set Python executable path


    QApplication a(argc, argv);
    MainWindow w;
    w.show();
    return a.exec();
}
