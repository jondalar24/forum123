"""Este script limpia las ejecuciones antiguas de flujos de trabajo de GitHub para ramas eliminadas.

No tiene sentido mantener estas ejecuciones, ya que están relacionadas con commits inexistentes de ramas inexistentes. Dado que las ejecuciones de este flujo de trabajo permanecerán después de cada rama eliminada, también queremos limpiarlas, por eso este script elimina las ejecuciones no solo para ramas eliminadas, sino también las ejecuciones antiguas de este flujo de trabajo. Esto significa que siempre tendremos solo una ejecución de este flujo de trabajo: la ejecución para la rama eliminada más reciente.

Este script está destinado a ejecutarse en un flujo de trabajo de GitHub, que proporcionará las variables de entorno que necesitamos.
"""

import os

from github import Github


GITHUB_EVENT_REF = os.environ["GITHUB_EVENT_REF"]  # referencia completa de una rama eliminada, por ejemplo: 'refs/heads/main'
GITHUB_REPOSITORY = os.environ["GITHUB_REPOSITORY"]  # el nombre del propietario y del repositorio, por ejemplo: 'octocat/Hello-World'
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]  # token único para autenticar en una ejecución de flujo de trabajo, generado por GitHub

DELETED_BRANCH_NAME = GITHUB_EVENT_REF.split("/")[-1]


def main():
    repository = Github(GITHUB_TOKEN).get_repo(GITHUB_REPOSITORY)
    for run in repository.get_workflow_runs(branch=DELETED_BRANCH_NAME):
        run.delete()

    # limpiar también las ejecuciones antiguas de este flujo de trabajo
    for run in repository.get_workflow_runs(event="delete"):
        run.delete()


if __name__ == "__main__":
    main()
