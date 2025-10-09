#!/usr/bin/env python3
"""
Translation cards service for multi-language celiac disease communication
"""

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from PySide6.QtCore import QObject, Signal


@dataclass
class TranslationCard:
    """Translation card data structure"""
    language: str
    language_code: str
    message: str
    pronunciation: Optional[str] = None
    cultural_notes: Optional[str] = None


class TranslationCardsService(QObject):
    """Service for managing celiac disease translation cards"""
    
    # Signals
    translation_updated = Signal(str, str)  # language_code, message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.translation_cards = self._load_default_translations()
        self.custom_translations = {}
    
    def _load_default_translations(self) -> Dict[str, TranslationCard]:
        """Load default translation cards"""
        translations = {
            'en': TranslationCard(
                language="English",
                language_code="en",
                message="I have Celiac Disease, a serious autoimmune condition. I must eat strictly gluten-free to avoid getting sick. Gluten is a protein found in wheat, rye, and barley. Even tiny amounts — from shared surfaces, utensils, fryers, or cooking water — can cause a reaction. Can you please help me choose a safe gluten-free option? Thank you so much for your help — I really appreciate it!",
                pronunciation="I have SEEL-ee-ak disease...",
                cultural_notes="Direct communication style preferred in English-speaking countries."
            ),
            'es': TranslationCard(
                language="Spanish",
                language_code="es",
                message="Tengo enfermedad celíaca, una condición autoinmune grave. Debo comer estrictamente sin gluten para evitar enfermarme. El gluten es una proteína que se encuentra en el trigo, el centeno y la cebada. Incluso cantidades muy pequeñas — de superficies compartidas, utensilios, freidoras o agua de cocción — pueden causar una reacción. ¿Podrías ayudarme a elegir una opción segura sin gluten? ¡Muchas gracias por tu ayuda — realmente lo aprecio!",
                pronunciation="TEN-go en-fer-meh-DAD seh-LEE-ah-ka...",
                cultural_notes="Use formal 'usted' in formal settings, 'tú' in casual situations."
            ),
            'fr': TranslationCard(
                language="French",
                language_code="fr",
                message="J'ai la maladie cœliaque, une maladie auto-immune grave. Je dois manger strictement sans gluten pour éviter de tomber malade. Le gluten est une protéine présente dans le blé, le seigle et l'orge. Même de très petites quantités — provenant de surfaces partagées, d'ustensiles, de friteuses ou d'eau de cuisson — peuvent causer une réaction. Pouvez-vous m'aider à choisir une option sûre sans gluten ? Merci beaucoup pour votre aide — je l'apprécie vraiment !",
                pronunciation="ZHAY la ma-LEED say-lee-AK...",
                cultural_notes="Always use formal address in France. Be polite and patient."
            ),
            'de': TranslationCard(
                language="German",
                language_code="de",
                message="Ich habe Zöliakie, eine ernste Autoimmunerkrankung. Ich muss streng glutenfrei essen, um nicht krank zu werden. Gluten ist ein Protein, das in Weizen, Roggen und Gerste vorkommt. Selbst winzige Mengen — von geteilten Oberflächen, Utensilien, Frittiergeräten oder Kochwasser — können eine Reaktion verursachen. Können Sie mir bitte helfen, eine sichere glutenfreie Option zu wählen? Vielen Dank für Ihre Hilfe — ich schätze es wirklich sehr!",
                pronunciation="Ikh HA-beh tsö-li-AH-kee...",
                cultural_notes="Use formal 'Sie' in Germany. Direct but respectful communication."
            ),
            'it': TranslationCard(
                language="Italian",
                language_code="it",
                message="Ho la malattia celiaca, una condizione autoimmune grave. Devo mangiare rigorosamente senza glutine per evitare di ammalarmi. Il glutine è una proteina presente nel grano, nella segale e nell'orzo. Anche piccole quantità — da superfici condivise, utensili, friggitrici o acqua di cottura — possono causare una reazione. Potreste aiutarmi a scegliere un'opzione sicura senza glutine? Grazie mille per il vostro aiuto — lo apprezzo davvero!",
                pronunciation="OH la ma-LAT-tee-ah cheh-lee-AH-ka...",
                cultural_notes="Use formal 'Lei' in formal settings. Italians appreciate politeness."
            ),
            'pt': TranslationCard(
                language="Portuguese",
                language_code="pt",
                message="Tenho doença celíaca, uma condição autoimune séria. Devo comer estritamente sem glúten para evitar ficar doente. O glúten é uma proteína encontrada no trigo, centeio e cevada. Mesmo pequenas quantidades — de superfícies compartilhadas, utensílios, fritadeiras ou água de cozimento — podem causar uma reação. Você poderia me ajudar a escolher uma opção segura sem glúten? Muito obrigado pela sua ajuda — eu realmente agradeço!",
                pronunciation="TEN-yo do-EN-sa seh-LEE-ah-ka...",
                cultural_notes="Brazilian Portuguese: use 'você', European Portuguese: use 'tu' or formal address."
            ),
            'ja': TranslationCard(
                language="Japanese",
                language_code="ja",
                message="私はセリアック病という深刻な自己免疫疾患を患っています。病気を避けるために、厳格にグルテンフリーで食事をする必要があります。グルテンは小麦、ライ麦、大麦に含まれるタンパク質です。共有の表面、調理器具、フライヤー、または調理水からの微量でも反応を引き起こす可能性があります。安全なグルテンフリーの選択肢を選ぶのを手伝っていただけますか？ご協力いただき、本当にありがとうございます！",
                pronunciation="Watashi wa se-ri-AK-ku byou to iu shin-koku-na ji-ko-men-eki shikkan wo kan-ga-tte i-masu...",
                cultural_notes="Use polite forms (desu/masu). Bow slightly when speaking. Be very respectful."
            ),
            'zh': TranslationCard(
                language="Chinese (Simplified)",
                language_code="zh",
                message="我患有乳糜泻，这是一种严重的自身免疫性疾病。我必须严格无麸质饮食以避免生病。麸质是存在于小麦、黑麦和大麦中的蛋白质。即使是极少量——来自共享表面、器具、油炸锅或烹饪水——也可能引起反应。您能帮我选择一个安全的无麸质选择吗？非常感谢您的帮助——我真的很感激！",
                pronunciation="Wǒ huàn yǒu rǔ mí xiè, zhè shì yī zhǒng yán zhòng de zì shēn miǎn yì xìng jí bìng...",
                cultural_notes="Use formal address. Chinese culture values harmony and indirect communication."
            ),
            'ar': TranslationCard(
                language="Arabic",
                language_code="ar",
                message="لدي مرض الاضطرابات الهضمية، وهي حالة مناعية ذاتية خطيرة. يجب أن أتناول طعامًا خاليًا من الغلوتين بشكل صارم لتجنب المرض. الغلوتين هو بروتين موجود في القمح والجاودار والشعير. حتى الكميات الصغيرة جداً - من الأسطح المشتركة أو الأدوات أو المقليات أو ماء الطهي - يمكن أن تسبب رد فعل. هل يمكنك مساعدتي في اختيار خيار آمن خالٍ من الغلوتين؟ شكراً جزيلاً لمساعدتك - أقدر ذلك حقاً!",
                pronunciation="La-dee mar-AD al-idh-ti-RA-bat al-had-mi-ya...",
                cultural_notes="Use formal Arabic. Right-to-left script. Show respect for cultural dietary restrictions."
            ),
            'hi': TranslationCard(
                language="Hindi",
                language_code="hi",
                message="मुझे सीलिएक रोग है, जो एक गंभीर ऑटोइम्यून स्थिति है। बीमार होने से बचने के लिए मुझे सख्ती से ग्लूटेन-मुक्त भोजन करना चाहिए। ग्लूटेन गेहूं, राई और जौ में पाया जाने वाला प्रोटीन है। यहां तक कि बहुत कम मात्रा - साझा सतहों, बर्तनों, फ्रायर या पकाने के पानी से - प्रतिक्रिया का कारण बन सकती है। क्या आप मुझे एक सुरक्षित ग्लूटेन-मुक्त विकल्प चुनने में मदद कर सकते हैं? आपकी मदद के लिए बहुत धन्यवाद - मैं वास्तव में इसकी सराहना करता हूं!",
                pronunciation="Mujhe see-lee-ak rog hai, jo ek gam-bheer auto-immune sthiti hai...",
                cultural_notes="Use formal address. Indian culture has many dietary restrictions - be understanding."
            ),
            'ko': TranslationCard(
                language="Korean",
                language_code="ko",
                message="저는 심각한 자가면역 질환인 설탁병을 앓고 있습니다. 병에 걸리지 않기 위해 엄격하게 글루텐 프리 식단을 유지해야 합니다. 글루텐은 밀, 호밀, 보리에 포함된 단백질입니다. 공유 표면, 조리기구, 튀김기, 조리용 물에서 나오는 극소량이라도 반응을 일으킬 수 있습니다. 안전한 글루텐 프리 옵션을 선택하는 데 도움을 주실 수 있나요? 도움을 주셔서 정말 감사합니다!",
                pronunciation="Jeo-neun sim-gak-han ja-ga-myeon-yeok jil-hwan-in seol-tak-byeong-eul al-go it-seum-ni-da...",
                cultural_notes="Use polite forms. Korean culture values respect and harmony."
            ),
            'ru': TranslationCard(
                language="Russian",
                language_code="ru",
                message="У меня целиакия, серьезное аутоиммунное заболевание. Я должен строго придерживаться безглютеновой диеты, чтобы не заболеть. Глютен — это белок, содержащийся в пшенице, ржи и ячмене. Даже крошечные количества — от общих поверхностей, посуды, фритюрниц или воды для приготовления — могут вызвать реакцию. Не могли бы вы помочь мне выбрать безопасный безглютеновый вариант? Большое спасибо за вашу помощь — я действительно это ценю!",
                pronunciation="U me-nya tse-li-A-kee-ya, se-ryez-no-ye a-u-to-im-mun-no-ye za-bo-le-va-ni-ye...",
                cultural_notes="Use formal address. Russian culture appreciates direct but polite communication."
            ),
            'nl': TranslationCard(
                language="Dutch",
                language_code="nl",
                message="Ik heb coeliakie, een ernstige auto-immuunziekte. Ik moet strikt glutenvrij eten om niet ziek te worden. Gluten is een eiwit dat voorkomt in tarwe, rogge en gerst. Zelfs kleine hoeveelheden — van gedeelde oppervlakken, keukengerei, friteuses of kookwater — kunnen een reactie veroorzaken. Kunt u mij helpen een veilige glutenvrije optie te kiezen? Heel erg bedankt voor uw hulp — ik waardeer het echt!",
                pronunciation="Ik heb ko-lee-AH-kee, een ern-STEE-ge ow-to-im-MUUN-ziek-te...",
                cultural_notes="Use formal 'u' in Netherlands. Dutch people appreciate directness."
            ),
            'sv': TranslationCard(
                language="Swedish",
                language_code="sv",
                message="Jag har celiaki, en allvarlig autoimmun sjukdom. Jag måste äta strikt glutenfritt för att inte bli sjuk. Gluten är ett protein som finns i vete, råg och korn. Även små mängder — från delade ytor, köksredskap, fritörer eller kokvatten — kan orsaka en reaktion. Kan ni hjälpa mig välja en säker glutenfri alternativ? Tack så mycket för er hjälp — jag uppskattar verkligen det!",
                pronunciation="Yag har se-lee-AH-kee, en al-VAHR-lig ow-to-im-MUUN shuk-DOM...",
                cultural_notes="Use formal address. Swedish culture values equality and directness."
            ),
            'no': TranslationCard(
                language="Norwegian",
                language_code="no",
                message="Jeg har cøliaki, en alvorlig autoimmun sykdom. Jeg må spise strengt glutenfritt for ikke å bli syk. Gluten er et protein som finnes i hvete, rug og bygg. Selv små mengder — fra delte overflater, kjøkkenredskaper, fritører eller kokevann — kan forårsake en reaksjon. Kan dere hjelpe meg å velge et trygt glutenfritt alternativ? Tusen takk for hjelpen — jeg setter stor pris på det!",
                pronunciation="Yay har se-lee-AH-kee, en al-VOR-lig ow-to-im-MUUN syk-DOM...",
                cultural_notes="Use formal address. Norwegian culture is similar to Swedish."
            ),
            'da': TranslationCard(
                language="Danish",
                language_code="da",
                message="Jeg har cøliaki, en alvorlig autoimmun sygdom. Jeg skal spise strengt glutenfrit for ikke at blive syg. Gluten er et protein, der findes i hvede, rug og byg. Selv små mængder — fra delte overflader, køkkenredskaber, fritureer eller kogevand — kan forårsage en reaktion. Kan I hjælpe mig med at vælge et sikkert glutenfrit alternativ? Mange tak for jeres hjælp — jeg sætter stor pris på det!",
                pronunciation="Yay har se-lee-AH-kee, en al-VOR-lig ow-to-im-MUUN syk-DOM...",
                cultural_notes="Use formal address. Danish culture values directness and equality."
            )
        }
        
        return translations
    
    def get_translation_card(self, language_code: str) -> Optional[TranslationCard]:
        """Get translation card for specified language"""
        # Check custom translations first
        if language_code in self.custom_translations:
            return self.custom_translations[language_code]
        
        # Return default translation
        return self.translation_cards.get(language_code.lower())
    
    def get_available_languages(self) -> List[str]:
        """Get list of available language codes"""
        all_languages = list(self.translation_cards.keys()) + list(self.custom_translations.keys())
        return sorted(set(all_languages))
    
    def get_language_name(self, language_code: str) -> str:
        """Get human-readable language name"""
        card = self.get_translation_card(language_code)
        return card.language if card else language_code
    
    def add_custom_translation(self, language_code: str, translation_card: TranslationCard) -> bool:
        """Add custom translation card"""
        try:
            self.custom_translations[language_code.lower()] = translation_card
            self.translation_updated.emit(language_code, translation_card.message)
            return True
        except Exception as e:
            print(f"Error adding custom translation: {e}")
            return False
    
    def update_translation(self, language_code: str, new_message: str, 
                          pronunciation: Optional[str] = None,
                          cultural_notes: Optional[str] = None) -> bool:
        """Update existing translation"""
        try:
            existing_card = self.get_translation_card(language_code)
            if existing_card:
                updated_card = TranslationCard(
                    language=existing_card.language,
                    language_code=language_code,
                    message=new_message,
                    pronunciation=pronunciation or existing_card.pronunciation,
                    cultural_notes=cultural_notes or existing_card.cultural_notes
                )
                
                self.custom_translations[language_code.lower()] = updated_card
                self.translation_updated.emit(language_code, new_message)
                return True
            return False
        except Exception as e:
            print(f"Error updating translation: {e}")
            return False
    
    def remove_custom_translation(self, language_code: str) -> bool:
        """Remove custom translation"""
        try:
            if language_code.lower() in self.custom_translations:
                del self.custom_translations[language_code.lower()]
                return True
            return False
        except Exception as e:
            print(f"Error removing custom translation: {e}")
            return False
    
    def export_translations(self, file_path: str, include_custom: bool = True) -> bool:
        """Export translations to JSON file"""
        try:
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'translations': {}
            }
            
            # Export default translations
            for code, card in self.translation_cards.items():
                export_data['translations'][code] = {
                    'language': card.language,
                    'language_code': card.language_code,
                    'message': card.message,
                    'pronunciation': card.pronunciation,
                    'cultural_notes': card.cultural_notes,
                    'is_custom': False
                }
            
            # Export custom translations if requested
            if include_custom:
                for code, card in self.custom_translations.items():
                    export_data['translations'][code] = {
                        'language': card.language,
                        'language_code': card.language_code,
                        'message': card.message,
                        'pronunciation': card.pronunciation,
                        'cultural_notes': card.cultural_notes,
                        'is_custom': True
                    }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error exporting translations: {e}")
            return False
    
    def import_translations(self, file_path: str, overwrite_existing: bool = False) -> int:
        """Import translations from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            imported_count = 0
            
            for code, data in import_data.get('translations', {}).items():
                # Skip if already exists and not overwriting
                if not overwrite_existing and code.lower() in self.custom_translations:
                    continue
                
                translation_card = TranslationCard(
                    language=data.get('language', ''),
                    language_code=data.get('language_code', code),
                    message=data.get('message', ''),
                    pronunciation=data.get('pronunciation'),
                    cultural_notes=data.get('cultural_notes')
                )
                
                if self.add_custom_translation(code, translation_card):
                    imported_count += 1
            
            return imported_count
            
        except Exception as e:
            print(f"Error importing translations: {e}")
            return 0
    
    def get_translation_statistics(self) -> Dict[str, Any]:
        """Get translation statistics"""
        return {
            'total_languages': len(self.translation_cards) + len(self.custom_translations),
            'default_translations': len(self.translation_cards),
            'custom_translations': len(self.custom_translations),
            'available_languages': self.get_available_languages()
        }
    
    def search_translations(self, search_term: str) -> List[TranslationCard]:
        """Search translations by content"""
        results = []
        search_term_lower = search_term.lower()
        
        # Search in default translations
        for card in self.translation_cards.values():
            if (search_term_lower in card.message.lower() or
                search_term_lower in card.language.lower() or
                (card.pronunciation and search_term_lower in card.pronunciation.lower())):
                results.append(card)
        
        # Search in custom translations
        for card in self.custom_translations.values():
            if (search_term_lower in card.message.lower() or
                search_term_lower in card.language.lower() or
                (card.pronunciation and search_term_lower in card.pronunciation.lower())):
                results.append(card)
        
        return results


# Global translation cards service instance
_translation_cards_service = None


def get_translation_cards_service() -> TranslationCardsService:
    """Get global translation cards service"""
    global _translation_cards_service
    if _translation_cards_service is None:
        _translation_cards_service = TranslationCardsService()
    return _translation_cards_service
