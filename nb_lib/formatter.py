import os
import nbformat
from nbconvert import MarkdownExporter, PDFExporter, RSTExporter
from nbconvert.writers import FilesWriter

SUPPORTED_FORMATS = {"md", "pdf", "rst"}


class Formatter:
    def __init__(self, output):
        assert output in SUPPORTED_FORMATS, f"supported formats are {SUPPORTED_FORMATS}"
        self.read_encoding = "utf-8"
        self.write_encoding = "utf-8"
        self.format = output

        if self.format == "pdf":
            pdf = PDFExporter()
            pdf.exclude_output_prompt = True
            pdf.exclude_input = True
            self.exporter = pdf
        elif self.format == "rst":
            self.exporter = RSTExporter()
        else:
            self.exporter = MarkdownExporter()

    def dst_folder(self, file):
        filePath = file.split("/")[0:-1]
        return "/".join(filePath) + "/" if len(filePath) > 0 else ""

    def dest_file(self, file, withFormat=True):
        return file.split("/")[-1].replace(".ipynb", "." + self.format if withFormat else "")

    def dst_path(self, file):
        return self.dst_folder(file) + self.dest_file(file)

    def convert(self, file):
        assert os.path.exists(file), f"this should not happen, path {file} must exist"
        body, resources = self.export(file)

        fw = FilesWriter()
        fw._makedir(self.dst_folder(file))
        fw.build_directory = self.dst_folder(file)
        fw.write(body, resources, notebook_name=self.dest_file(file, withFormat=False))

    def export(self, file):
        with open(file, "r", encoding=self.read_encoding) as f:
            nb = nbformat.read(f, as_version=4)
            body, resources = self.exporter.from_notebook_node(nb)
            return body, resources

    def needs_format(self, file):
        f_path = self.dst_path(file)

        if not os.path.exists(f_path):
            return True

        notebook_modified = os.stat(file).st_mtime
        formatted_modified = os.stat(f_path).st_mtime

        return notebook_modified > formatted_modified

    def save_figures(self, resources):
        if "outputs" not in resources:
            return

        for name, bytes_ in resources["outputs"]:
            print(f"name = {name}, bytes = {len(bytes_)}")

        for key, value in resources.items():
            pass
