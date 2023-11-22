import logging
import pathlib
from jinja2 import Environment, FileSystemLoader, UndefinedError, StrictUndefined

current_folder = pathlib.Path(__file__).parent.resolve()
issue_template_folder = current_folder / "issue_template"
diction_folder = current_folder.parents[1] / "dictions"


def configure_template(jinja_template_path: pathlib.Path, diction_folder: pathlib.Path) -> str:
    environment = Environment(
        loader=FileSystemLoader(jinja_template_path.parent), undefined=StrictUndefined)
    jinja_template = environment.get_template(jinja_template_path.name)

    # load dictions
    dictions = {}
    for d in diction_folder.glob("diction_*.md"):
        diction_name = d.stem.replace("diction_", "").upper()
        dictions[diction_name] = d.read_text()

    try:
        rendered_template = jinja_template.render(dictions)
    except UndefinedError as e:
        raise ValueError(f'Missing diction: {e}')

    logging.info(f"Configured template {jinja_template_path}")

    return rendered_template


def configure_all_issue_templates(issue_template_folder: str | pathlib.Path) -> None:

    for template_file in pathlib.Path(issue_template_folder).glob("*.yml"):
        template = configure_template(template_file, diction_folder)
        save_path = current_folder / ".." / "ISSUE_TEMPLATE" / template_file.name
        pathlib.Path(save_path).write_text(template)


if __name__ == "__main__":
    configure_all_issue_templates(issue_template_folder)
