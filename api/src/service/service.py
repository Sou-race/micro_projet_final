

from api.src.model.model import ModelResponseToFront

#juste un test pour voir que tout marche dans ressource
def test():
    res =ModelResponseToFront(
        name="test",
        accuracies=[0.1, 0.2, 0.3],
        isFinished=True
    )
    return res
