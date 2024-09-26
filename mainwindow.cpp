#include <pybind11/pybind11.h>
#include <pybind11/embed.h>
#include <iostream>
#include <QDir>

#include "mainwindow.h"
#include "ui_mainwindow.h"
#include "QFileDialog"
#include "QMessageBox"




namespace py = pybind11;

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::MainWindow)
{
    QDir currentDir = QDir::current();
    currentDir.setPath(QDir::homePath());
    qDebug() << "Current app directory: " << currentDir.path();
    QDir::setCurrent(currentDir.path());
    ui->setupUi(this);
    connect(ui->browseButton, &QPushButton::clicked, this, &MainWindow::browseLibrary);
    connect(ui->generateButton, &QPushButton::clicked, this, &MainWindow::generateSchedule);
}

MainWindow::~MainWindow()
{
    delete ui;
}

void MainWindow::browseLibrary()
{
    QStringList filenames = QFileDialog::getOpenFileNames(
        this,
        "Select CSV Files",
        "",
        "CSV Files (*.csv);;All Files (*)"
        );

    if (!filenames.isEmpty()) {

        for (int i = 0; i < filenames.size(); i++) {
            std::cout << filenames[i].toStdString() << std::endl; // Check full names in console
        }

        fullFilePaths = filenames;
        ui->listWidget->clear(); // Clear up before adding the items

        QFont customFont;
        customFont.setPointSize(14);  // Set the font size
        customFont.setBold(true);     // Make the font bold


        for (const QString &filePath: filenames) {
            QFileInfo fileInfo(filePath);
            QString filename = fileInfo.dir().dirName() + "/" + fileInfo.fileName();

            QListWidgetItem *listItem = new QListWidgetItem(filename);

            listItem->setFont(customFont);

            ui->listWidget->addItem(listItem);
        }
    }
}


void MainWindow::generateSchedule()
{
    QString folderPath = QFileDialog::getSaveFileName(
        this,
        "Choose folder and name to save Schedule",
        ""
        );
    if (!folderPath.isEmpty()) {
        // QMessageBox::information(this, "Info", "Generating Schedule...");
        qDebug() << "Generating Schedule...";
    }
    QStringList filePaths = fullFilePaths;


    try {

        py::module_ PythonScript = py::module_::import("main");

        py::list pyFileNames; // Convert list of QStrings to python list
        for (const QString &filename : filePaths) {
            pyFileNames.append(filename.toStdString());
        }

        std::string outputFolder = folderPath.toStdString();

        py::object result = PythonScript.attr("generate_excel")(pyFileNames, outputFolder);

        std::string outputPath = result.cast<std::string>();

        QMessageBox::information(this, "Success", "Schedule Generated: " + QString::fromStdString(outputPath));

        // Execute the script by calling its __main__ function (this will run the script)

        // py::exec("import FrontDeskSolver.main");  // This executes the script

    } catch (const std::exception &e) {
        QMessageBox::critical(this, "Error", e.what());
    }
}

