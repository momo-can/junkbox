# -*- coding: utf-8 -*-
import copy
from maya import cmds

__author__ = 'masahiro ohmomo'


def getSkinCluster(name=''):
    """Get skin cluster from the mesh.

    Args:
        name (str, optional): Specify a transform name.
        Defaults to ''.

    Returns:
        str: Returns the skin cluster name.
    """
    results = []

    if cmds.nodeType(name) == 'transform':
        name = cmds.listRelatives(
            name,
            shapes=True,
            fullPath=True
        ) or []

    if not name:
        return results

    for o in name:
        results = cmds.listConnections(
            o,
            type='skinCluster',
            destination=False,
            source=True,
            connections=False,
            plugs=False
        ) or []
        if results:
            break

    if not results:
        return None

    if isinstance(results, list):
        results = results[0]
    return results


def getInfluence(name=''):
    """Get influence from the skin cluster.

    Args:
        name (str, optional): Specify a skin cluster.
        Defaults to ''.

    Returns:
        list: Returns a list of joints.
    """
    results = []

    if not name:
        return results

    sc = getSkinCluster(name=name)
    if not sc:
        return results

    results = cmds.skinCluster(
        sc,
        query=True,
        influence=True
    ) or []

    return results


def getUVSet(name=''):
    """Get uv set from an name.

    Args:
        name (str, optional): Specify a transform name.
        Defaults to ''.

    Returns:
        list: Returns a list of uv sets.
    """
    result = []
    if not name:
        return result

    if cmds.nodeType(name) == 'transform':
        name = cmds.listRelatives(
            name,
            shapes=True,
            fullPath=True
        ) or []

    result = cmds.polyUVSet(
        name,
        query=True,
        allUVSets=True
    ) or []

    return result


def main(
    dropoffRate=4.0,
    maximumInfluences=5,
    userSourceUVSet='',
    userDestinationUVSet=''
):
    """Set the bind skin and copy weight.

    Args:
        dropoffRate (float, optional): Specify drop-off rate.
        Defaults to 4.0.

        maximumInfluences (int, optional): Specify the maximum influences.
        Defaults to 5.

        userSourceUVSet (str, optional): Specify the source uv name.
        Defaults to ''.

        userDestinationUVSet (str, optional): Specify the destination uv name.
        Defaults to ''.
    """
    selection = cmds.ls(selection=True, long=True) or []
    if len(selection) < 2:
        cmds.error('Select two objects. The reference and target meshes.')
        return

    sourceObject = selection[0]
    destinationObject = selection[1]

    # Get each skin cluster.
    sourceInfluence = getInfluence(name=sourceObject)
    destinationInfluence = getInfluence(name=destinationObject)

    # Remove the target skin cluster.
    if destinationInfluence:
        cmds.skinCluster(destinationObject, edit=True, unbind=True)

    # Bind.
    objects = []
    objects = copy.deepcopy(sourceInfluence)
    objects.insert(0, destinationObject)
    kwargs = {
        'dropoffRate': dropoffRate,
        'removeUnusedInfluence': False,
        'maximumInfluences': maximumInfluences,
        'bindMethod': 0,
        'toSelectedBones': True,
        'toSkeletonAndTransforms': False
    }
    cmds.skinCluster(objects, **kwargs)

    # Copy weight.
    sourceSkin = getSkinCluster(name=sourceObject)
    destinationSkin = getSkinCluster(name=destinationObject)
    sourceUVSet = getUVSet(name=sourceObject)
    destinationUVSet = getUVSet(name=destinationObject)

    sourceMessage = 'UV is not set on the source mesh.\n'
    sourceMessage += 'The copy process has been cancelled.'
    if userSourceUVSet and userSourceUVSet in sourceUVSet:
        sourceUVSet = userSourceUVSet
    elif userSourceUVSet and not userSourceUVSet in sourceUVSet:
        cmds.warning(sourceMessage)
        return

    if not sourceUVSet:
        cmds.warning(sourceMessage)
        return
    if isinstance(sourceUVSet, list):
        sourceUVSet = sourceUVSet[0]

    destinationMessage = 'UV is not set on the destination mesh.\n'
    destinationMessage += 'The copy process has been cancelled.'
    if userDestinationUVSet and userDestinationUVSet in destinationUVSet:
        destinationUVSet = userDestinationUVSet
    elif userDestinationUVSet and not userDestinationUVSet in destinationUVSet:
        cmds.warning(destinationMessage)
        return

    if not sourceUVSet:
        cmds.warning(destinationMessage)
        return
    if isinstance(destinationUVSet, list):
        destinationUVSet = destinationUVSet[0]

    cmds.copySkinWeights(
        sourceSkin=sourceSkin,
        destinationSkin=destinationSkin,
        noMirror=True,
        surfaceAssociation='closestPoint',
        uvSpace=[sourceUVSet, destinationUVSet],
        influenceAssociation=['label', 'oneToOne', 'closestJoint']
    )

    cmds.select(selection, r=True)

"""
How to use.

import bindAndCopyWeight
bindAndCopyWeight.main()

"""
