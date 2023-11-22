import logging
import pathlib
from jinja2 import Environment, FileSystemLoader, UndefinedError

current_folder = pathlib.Path(__file__).parent.resolve()
issue_template_folder = current_folder / "issue_template"


def configure_template(jinja_template_path: str | pathlib.Path) -> str:
    environment = Environment(
        loader=FileSystemLoader(jinja_template_path.parent))
    jinja_template = environment.get_template(jinja_template_path.name)

    # load dictons
    dictons = {}
    for d in pathlib.Path(".").glob("dicton_*.md"):
        dicton_name = d.replace("dicton_", "").replace(".md", "")
        dictons[dicton_name] = d.read_text()

    try:
        rendered_template = jinja_template.render(dictons)
    except UndefinedError as e:
        raise ValueError(f'Missing dicton: {e}')

    logging.info(f"Configured template {jinja_template_path}")

    return rendered_template


def configure_all_issue_templates(issue_template_folder: str | pathlib.Path) -> None:

    for template_file in pathlib.Path(issue_template_folder).glob("*.yml"):
        template = configure_template(template_file)
        save_path = current_folder / ".." / "ISSUE_TEMPLATE" / template_file.name
        pathlib.Path(save_path).write_text(template)


if __name__ == "__main__":
    configure_all_issue_templates(issue_template_folder)
