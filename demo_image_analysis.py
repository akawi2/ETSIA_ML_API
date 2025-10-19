"""
Script de Démonstration - Analyse d'Images
Teste le modèle de détection de contenu sensible
"""
import sys
from pathlib import Path
from PIL import Image
import io

# Ajouter le dossier parent au path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.sensitive_image_caption import SensitiveImageCaptionModel


def create_test_image(color='white', size=(224, 224), save_path=None):
    """Crée une image de test"""
    img = Image.new('RGB', size, color=color)
    
    if save_path:
        img.save(save_path)
        print(f"✓ Image de test créée: {save_path}")
    
    return img


def analyze_image(model, image_path=None, image=None):
    """Analyse une image"""
    print("\n" + "="*70)
    
    if image_path:
        print(f"📸 Analyse de l'image: {image_path}")
        image = Image.open(image_path).convert("RGB")
    elif image:
        print(f"📸 Analyse de l'image (PIL)")
    else:
        raise ValueError("Fournir image_path ou image")
    
    print("-"*70)
    
    # Prédire
    result = model.predict(image=image)
    
    # Afficher les résultats
    print(f"\n🎯 RÉSULTAT :")
    print(f"  • Prédiction : {result['prediction']}")
    print(f"  • Confiance  : {result['confidence']:.2%}")
    print(f"  • Sévérité   : {result['severity']}")
    print(f"  • Sûr        : {'✅ OUI' if result['is_safe'] else '⚠️ NON'}")
    
    print(f"\n📝 LÉGENDES :")
    print(f"  • Anglais    : {result['caption_en']}")
    print(f"  • Français   : {result['caption_fr']}")
    
    print(f"\n💡 EXPLICATION :")
    print(f"  {result['reasoning']}")
    
    print("="*70)
    
    return result


def main():
    """Fonction principale"""
    print("\n" + "🖼️  DÉMONSTRATION - ANALYSE D'IMAGES")
    print("="*70)
    
    # 1. Initialiser le modèle
    print("\n📦 Initialisation du modèle...")
    print("-"*70)
    
    try:
        model = SensitiveImageCaptionModel()
        print(f"✓ Modèle initialisé : {model.model_name} v{model.model_version}")
        print(f"✓ Device           : {model.device}")
        print(f"✓ Auteur           : {model.author}")
    except Exception as e:
        print(f"✗ Erreur d'initialisation : {e}")
        print("\n💡 Vérifiez que les dépendances sont installées :")
        print("   pip install transformers torch Pillow sentencepiece")
        return
    
    # 2. Test avec image générée
    print("\n🧪 TEST 1 : Image Générée (Blanc)")
    test_image = create_test_image(color='white')
    analyze_image(model, image=test_image)
    
    # 3. Test avec vos images (si fournies)
    if len(sys.argv) > 1:
        for image_path in sys.argv[1:]:
            print(f"\n🧪 TEST : Votre Image")
            try:
                analyze_image(model, image_path=image_path)
            except Exception as e:
                print(f"✗ Erreur : {e}")
    else:
        print("\n💡 ASTUCE :")
        print("   Pour tester vos images :")
        print("   python demo_image_analysis.py image1.jpg image2.jpg")
    
    # 4. Test batch
    print("\n🧪 TEST 2 : Batch de 3 Images")
    print("-"*70)
    
    images = [
        create_test_image(color='red'),
        create_test_image(color='green'),
        create_test_image(color='blue')
    ]
    
    print("Traitement de 3 images en batch...")
    results = model.batch_predict(images=images)
    
    for i, result in enumerate(results, 1):
        print(f"\nImage {i}:")
        print(f"  • Prédiction : {result['prediction']}")
        print(f"  • Légende FR : {result['caption_fr']}")
        print(f"  • Sûr        : {'✅' if result['is_safe'] else '⚠️'}")
    
    # 5. Health check
    print("\n🏥 HEALTH CHECK")
    print("-"*70)
    health = model.health_check()
    print(f"Status : {health['status']}")
    print(f"Device : {health.get('device', 'N/A')}")
    
    # 6. Statistiques
    print("\n📊 STATISTIQUES")
    print("-"*70)
    print(f"Mots-clés sensibles : {len(model.SENSITIVE_KEYWORDS)}")
    print(f"Catégories          : Drogue, Violence, Sexe, Autres")
    
    print("\n✨ Démonstration terminée !")
    print("="*70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interruption par l'utilisateur")
    except Exception as e:
        print(f"\n✗ ERREUR : {e}")
        import traceback
        traceback.print_exc()
