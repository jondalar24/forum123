"""Este script limpia las ejecuciones antiguas de flujos de trabajo de GitHub para commits reescritos por force pushes de la rama.

Estamos utilizando la estrategia de rebase para las ramas de git y cada rama de características al final del trabajo se rebasea en la última versión de la rama de desarrollo y contiene solo un commit con la descripción de lo que se ha hecho para esta característica. Cuando los desarrolladores trabajan con sus ramas de características, empujan muchos commits de “trabajo en progreso”, y cada push desencadena una ejecución de flujo de trabajo de GitHub. Pero dado que todos estos commits serán reescritos al final, queremos mantener nuestra lista de ejecuciones de flujo de trabajo limpia y eliminar las ejecuciones anteriores que fueron desencadenadas por commits que no existen después del rebase.

Este script está destinado a ejecutarse en un flujo de trabajo de GitHub, que proporcionará las variables de entorno que necesitamos.
"""

import os
import subprocess

from github import Github


GITHUB_REF_NAME = os.environ["GITHUB_REF_NAME"]  # nombre de la referencia de la rama actual, por ejemplo: `feature-branch-1
GITHUB_REPOSITORY = os.environ["GITHUB_REPOSITORY"]  # el nombre del propietario y del repositorio, por ejemplo: 'octocat/Hello-World'
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]  # token único para autenticar en una ejecución de flujo de trabajo, generado por GitHub


def main():
    branch_commit_hashes = set(get_branch_commits())
    repository = Github(GITHUB_TOKEN).get_repo(GITHUB_REPOSITORY)
    for run in repository.get_workflow_runs(branch=GITHUB_REF_NAME):
        if run.head_sha not in branch_commit_hashes:
            run.delete()


def get_branch_commits():
    """Obtener hashes de los commits de la rama actual que no se han fusionado con develop."""
    cmd = subprocess.run(["git", "cherry", "origin/develop", GITHUB_REF_NAME], capture_output=True, encoding="utf-8")
    for output_line in cmd.stdout.strip("\n").split("\n"):
        commit_hash = output_line.split(" ")[-1]  # parse commit hash
        yield commit_hash


if __name__ == "__main__":
    main()
