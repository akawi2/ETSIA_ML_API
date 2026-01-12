"""
Modèle de détection de hate speech avec BERT multilingue
"""
from .hatecomment_bert_model import HateCommentBertModel
from .hatecomment_bert_monitored import HateCommentBertMonitored

__all__ = ['HateCommentBertModel', 'HateCommentBertMonitored']
