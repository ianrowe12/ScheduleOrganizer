QT       += core gui

greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

CONFIG += c++17

# You can make your code fail to compile if it uses deprecated APIs.
# In order to do so, uncomment the following line.
#DEFINES += QT_DISABLE_DEPRECATED_BEFORE=0x060000    # disables all the APIs deprecated before Qt 6.0.0

ICON = CARES.icns

SOURCES += \
    main.cpp \
    mainwindow.cpp

HEADERS += \
    mainwindow.h

FORMS += \
    mainwindow.ui

# INCLUDEPATH += $$PWD/pybind11/include/
INCLUDEPATH += /Library/Python/3.9/site-packages/pybind11/include

# Add the pybind11 include path
# Include path for Python headers
INCLUDEPATH += /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Headers

# Link to the Python 3.9 library
LIBS += -L/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib -lpython3.9

# Add macOS-specific flag for dynamic symbol lookup
QMAKE_LFLAGS += -undefined dynamic_lookup
QMAKE_RPATHDIR += /Library/Developer/CommandLineTools/Library/Frameworks






# Default rules for deployment.
qnx: target.path = /tmp/$${TARGET}/bin
else: unix:!android: target.path = /opt/$${TARGET}/bin
!isEmpty(target.path): INSTALLS += target
