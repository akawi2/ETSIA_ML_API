"""
Modèle YANSNET - Générateur de contenu pour le réseau social
"""
from typing import Dict, Any, List
from app.core.base_model import BaseMLModel
from app.services.yansnet_llm.llm_predictor import get_llm_predictor
from app.config import settings
from app.utils.logger import setup_logger
import random
import json

logger = setup_logger(__name__)


class YansnetContentGeneratorModel(BaseMLModel):
    """
    Générateur de posts et commentaires pour peupler l'interface YANSNET.
    
    Utilise le même LLM que le système de détection pour créer du contenu
    réaliste pour les démos et tests d'interface.
    
    Note: Ce modèle ne fait PAS de détection, il GÉNÈRE du contenu.
    """
    
    # Configuration des types de posts
    POST_TYPES = [
        "confession", "coup de gueule", "demande d'aide",
        "message de soutien", "blague", "information utile"
    ]
    
    SENTIMENTS = ["positif", "neutre", "négatif"]
    
    TOPICS = [
        "les partiels stressants", "la vie en résidence universitaire",
        "le stage de fin d'études", "les associations étudiantes",
        "le planning des cours", "les notes et résultats",
        "les échanges internationaux", "le covoiturage pour l'école",
        "la cantine de l'école", "les problèmes de logement",
        "le stress avant les examens", "les fêtes étudiantes",
        "les relations étudiants-professeurs", "la recherche de mentors",
        "les concours de programmation", "le hackathon de l'école",
        "les voyages d'études", "les bourses et financements",
        "le nouveau bâtiment sportif", "les salles d'étude bondées"
    ]
    
    @property
    def model_name(self) -> str:
        return "yansnet-content-generator"
    
    @property
    def model_version(self) -> str:
        return "1.0.0"
    
    @property
    def author(self) -> str:
        return "Équipe YANSNET"
    
    @property
    def description(self) -> str:
        provider = settings.LLM_PROVIDER
        return f"Générateur de contenu pour YANSNET (LLM: {provider})"
    
    @property
    def tags(self) -> List[str]:
        return ["generator", "content", "yansnet", "demo"]
    
    def __init__(self):
        """Initialise le générateur avec le LLM existant"""
        try:
            self.predictor = get_llm_predictor()
            self._initialized = True
            logger.info(f"✓ {self.model_name} initialisé avec succès")
        except Exception as e:
            logger.error(f"✗ Erreur d'initialisation de {self.model_name}: {e}")
            self._initialized = False
            raise
    
    def predict(self, text: str, **kwargs) -> Dict[str, Any]:
        """
        Interface requise par BaseMLModel.
        
        Pour ce modèle, 'predict' génère du contenu au lieu de détecter.
        Le paramètre 'text' est ignoré, utilisez generate_post() à la place.
        """
        logger.warning(
            f"{self.model_name}.predict() appelé - "
            "Utilisez generate_post() ou generate_comment() à la place"
        )
        return self.generate_post()
    
    def generate_post(
        self,
        post_type: str = None,
        topic: str = None,
        sentiment: str = None
    ) -> Dict[str, Any]:
        """
        Génère un post pour le forum étudiant.
        
        Args:
            post_type: Type de post (optionnel, aléatoire si None)
            topic: Sujet du post (optionnel, aléatoire si None)
            sentiment: Sentiment du post (optionnel, auto si None)
        
        Returns:
            Dict avec le post généré
        """
        if not self._initialized:
            raise RuntimeError(f"{self.model_name} n'est pas initialisé")
        
        # Sélection aléatoire si non spécifié
        post_type = post_type or random.choice(self.POST_TYPES)
        topic = topic or random.choice(self.TOPICS)
        
        # Déterminer le sentiment selon le type
        if sentiment is None:
            sentiment = self._auto_sentiment(post_type)
        
        # Construire le prompt
        system_prompt = (
            "Tu es un assistant qui génère des publications réalistes "
            "pour un forum d'école d'ingénieurs. Génère du contenu crédible, "
            "naturel, sans marqueurs artificiels. Réponds UNIQUEMENT avec le texte "
            "du post, sans préfixes ni métadonnées."
        )
        
        user_prompt = (
            f"Génère un post de type '{post_type}' sur le sujet '{topic}', "
            f"avec un sentiment '{sentiment}'. "
            f"Minimum 3 phrases, style étudiant naturel, crédible."
        )
        
        try:
            # Appeler le LLM
            content = self._call_llm(system_prompt, user_prompt)
            
            return {
                "prediction": "POST_GENERATED",  # Pour compatibilité interface
                "confidence": 1.0,
                "severity": "Aucune",
                "content": content,
                "post_type": post_type,
                "topic": topic,
                "sentiment": sentiment
            }
            
        except Exception as e:
            logger.error(f"Erreur génération post: {e}")
            raise
    
    def generate_comment(
        self,
        post_content: str,
        sentiment: str = None,
        num_comments: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Génère des commentaires pour un post donné.
        
        Args:
            post_content: Contenu du post original
            sentiment: Sentiment souhaité (optionnel, naturel si None)
            num_comments: Nombre de commentaires à générer
        
        Returns:
            Liste de commentaires générés
        """
        if not self._initialized:
            raise RuntimeError(f"{self.model_name} n'est pas initialisé")
        
        comments = []
        
        for i in range(num_comments):
            # Sentiment aléatoire si non spécifié
            comment_sentiment = sentiment or random.choice(self.SENTIMENTS)
            
            system_prompt = (
                "Tu es un assistant qui génère des commentaires réalistes "
                "sur un forum étudiant. Génère des réponses naturelles, crédibles, "
                "sans marqueurs artificiels. Réponds UNIQUEMENT avec le texte "
                "du commentaire, sans préfixes."
            )
            
            user_prompt = (
                f"Post original: \"{post_content}\"\n\n"
                f"Génère un commentaire avec sentiment '{comment_sentiment}', "
                f"au moins 2 phrases, naturel et pertinent au post."
            )
            
            try:
                content = self._call_llm(system_prompt, user_prompt)
                
                comments.append({
                    "content": content,
                    "sentiment": comment_sentiment,
                    "comment_number": i + 1
                })
                
            except Exception as e:
                logger.error(f"Erreur génération commentaire {i+1}: {e}")
                # Continuer avec les autres commentaires
                comments.append({
                    "content": f"[Erreur de génération: {str(e)}]",
                    "sentiment": "neutre",
                    "comment_number": i + 1
                })
        
        return comments
    
    def generate_post_with_comments(
        self,
        post_type: str = None,
        topic: str = None,
        num_comments: int = None
    ) -> Dict[str, Any]:
        """
        Génère un post complet avec ses commentaires.
        
        Args:
            post_type: Type de post (optionnel)
            topic: Sujet (optionnel)
            num_comments: Nombre de commentaires (optionnel, 8-12 si None)
        
        Returns:
            Dict avec post et commentaires
        """
        # Générer le post
        post = self.generate_post(post_type=post_type, topic=topic)
        
        # Nombre aléatoire de commentaires
        if num_comments is None:
            num_comments = random.randint(8, 12)
        
        # Générer les commentaires
        comments = self.generate_comment(
            post_content=post["content"],
            num_comments=num_comments
        )
        
        return {
            "post": post,
            "comments": comments,
            "total_comments": len(comments)
        }
    
    def _auto_sentiment(self, post_type: str) -> str:
        """Détermine automatiquement le sentiment selon le type de post"""
        sentiment_map = {
            "coup de gueule": "négatif",
            "message de soutien": "positif",
            "blague": random.choice(["positif", "neutre"]),
            "information utile": "neutre",
            "confession": random.choice(["positif", "négatif"]),
            "demande d'aide": random.choice(self.SENTIMENTS)
        }
        return sentiment_map.get(post_type, random.choice(self.SENTIMENTS))
    
    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """
        Appelle le LLM pour générer du texte.
        
        Note: Utilise une approche différente du predictor car on veut
        du texte brut, pas une analyse JSON.
        """
        provider = settings.LLM_PROVIDER.lower()
        
        if provider == "gpt":
            return self._call_gpt(system_prompt, user_prompt)
        elif provider == "claude":
            return self._call_claude(system_prompt, user_prompt)
        elif provider == "local":
            return self._call_local(system_prompt, user_prompt)
        else:
            raise ValueError(f"Provider non supporté: {provider}")
    
    def _call_gpt(self, system_prompt: str, user_prompt: str) -> str:
        """Appel GPT pour génération de texte"""
        from openai import OpenAI
        
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.9,  # Plus créatif pour la génération
            max_tokens=500
        )
        
        return response.choices[0].message.content.strip()
    
    def _call_claude(self, system_prompt: str, user_prompt: str) -> str:
        """Appel Claude pour génération de texte"""
        import anthropic
        
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        
        message = client.messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=1024,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        return message.content[0].text.strip()
    
    def _call_local(self, system_prompt: str, user_prompt: str) -> str:
        """Appel LLM local pour génération de texte"""
        import requests
        
        response = requests.post(
            f"{settings.OLLAMA_BASE_URL}/api/chat",
            json={
                "model": settings.OLLAMA_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "stream": False,
                "options": {
                    "temperature": 0.9,
                    "num_predict": 500
                }
            },
            timeout=120
        )
        response.raise_for_status()
        
        return response.json()['message']['content'].strip()
    
    def health_check(self) -> Dict[str, Any]:
        """Vérifie que le générateur est opérationnel"""
        try:
            # Test de génération simple
            result = self.generate_post(
                post_type="blague",
                topic="les partiels stressants"
            )
            
            return {
                "status": "healthy",
                "model": self.model_name,
                "version": self.model_version,
                "provider": settings.LLM_PROVIDER,
                "test_generation": "success",
                "content_length": len(result.get("content", ""))
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "model": self.model_name,
                "error": str(e)
            }
