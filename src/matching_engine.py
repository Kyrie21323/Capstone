"""
Intelligent Matching Engine for Event Attendees
Uses semantic similarity to match users based on keywords and document content
Offline method using sentence-transformers
"""

import os
import logging
from typing import List, Dict, Tuple, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import PyPDF2
from docx import Document

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MatchingEngine:
    def __init__(self):
        """Initialize the matching engine with the sentence transformer model"""
        try:
            # Use all-mpnet-base-v2 for high accuracy
            self.model = SentenceTransformer('all-mpnet-base-v2')
            logger.info("Sentence transformer model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load sentence transformer model: {e}")
            raise
    
    def extract_text_from_document(self, file_path: str) -> str:
        """
        Extract text content from various document formats
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Extracted text content
        """
        try:
            if not os.path.exists(file_path):
                logger.warning(f"File not found: {file_path}")
                return ""
            
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == '.pdf':
                return self._extract_pdf_text(file_path)
            elif file_extension in ['.doc', '.docx']:
                return self._extract_word_text(file_path)
            else:
                logger.warning(f"Unsupported file format: {file_extension}")
                return ""
                
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            return ""
    
    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF files"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            logger.error(f"Error reading PDF {file_path}: {e}")
            return ""
    
    def _extract_word_text(self, file_path: str) -> str:
        """Extract text from Word documents"""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error reading Word document {file_path}: {e}")
            return ""
    
    def preprocess_text(self, text: str) -> str:
        """
        Clean and preprocess text for better similarity matching
        
        Args:
            text: Raw text content
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Basic text cleaning
        text = text.lower().strip()
        
        # Remove excessive whitespace
        import re
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep alphanumeric and spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        
        return text.strip()
    
    def get_text_embedding(self, text: str) -> np.ndarray:
        """
        Convert text to semantic embedding vector
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        if not text:
            # Return zero vector for empty text
            return np.zeros(768)  # all-mpnet-base-v2 has 768 dimensions
        
        try:
            # Preprocess text
            cleaned_text = self.preprocess_text(text)
            
            # Generate embedding
            embedding = self.model.encode([cleaned_text])[0]
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return np.zeros(768)
    
    def calculate_keyword_similarity(self, keywords1: List[str], keywords2: List[str]) -> float:
        """
        Calculate semantic similarity between two sets of keywords
        
        Args:
            keywords1: First set of keywords
            keywords2: Second set of keywords
            
        Returns:
            Similarity score between 0 and 1
        """
        if not keywords1 or not keywords2:
            return 0.0
        
        try:
            # First check for exact keyword matches (boost score)
            keywords1_set = set(k.lower() for k in keywords1)
            keywords2_set = set(k.lower() for k in keywords2)
            exact_matches = len(keywords1_set.intersection(keywords2_set))
            
            if exact_matches > 0:
                # Boost score for exact matches
                exact_score = min(exact_matches / max(len(keywords1), len(keywords2)), 1.0)
                return max(exact_score, 0.3)  # Minimum 0.3 for exact matches
            
            # Convert keywords to text for semantic similarity
            text1 = ", ".join(keywords1)
            text2 = ", ".join(keywords2)
            
            # Get embeddings
            embedding1 = self.get_text_embedding(text1)
            embedding2 = self.get_text_embedding(text2)
            
            # Calculate cosine similarity
            similarity = cosine_similarity([embedding1], [embedding2])[0][0]
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating keyword similarity: {e}")
            return 0.0
    
    def calculate_document_similarity(self, doc_text1: str, doc_text2: str) -> float:
        """
        Calculate semantic similarity between two document texts
        
        Args:
            doc_text1: First document text
            doc_text2: Second document text
            
        Returns:
            Similarity score between 0 and 1
        """
        if not doc_text1 or not doc_text2:
            return 0.0
        
        try:
            # Get embeddings
            embedding1 = self.get_text_embedding(doc_text1)
            embedding2 = self.get_text_embedding(doc_text2)
            
            # Calculate cosine similarity
            similarity = cosine_similarity([embedding1], [embedding2])[0][0]
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating document similarity: {e}")
            return 0.0
    
    def calculate_match_score(self, user1_data: Dict, user2_data: Dict) -> float:
        """
        Calculate overall match score between two users
        Uses dynamic weighting based on document availability
        
        Args:
            user1_data: First user's data (keywords, document_text)
            user2_data: Second user's data (keywords, document_text)
            
        Returns:
            Overall match score between 0 and 1
        """
        try:
            # Check document availability
            user1_has_doc = bool(user1_data.get('document_text', '').strip())
            user2_has_doc = bool(user2_data.get('document_text', '').strip())
            
            # Calculate keyword similarity (always available)
            keyword_similarity = self.calculate_keyword_similarity(
                user1_data.get('keywords', []),
                user2_data.get('keywords', [])
            )
            
            # Determine weighting strategy based on document availability
            if not user1_has_doc and not user2_has_doc:
                # Both users have no documents - use keywords only
                total_score = keyword_similarity
                print(f"    📊 MATCHING ANALYSIS:")
                print(f"    ├─ Strategy: Keywords only (both users have no documents)")
                print(f"    ├─ Keyword similarity: {keyword_similarity:.4f}")
                print(f"    └─ Total score: {total_score:.4f}")
                
            elif user1_has_doc and not user2_has_doc:
                # User1 has document, User2 doesn't - compare keywords to document
                doc_similarity = self.calculate_document_similarity(
                    user1_data.get('document_text', ''),
                    ", ".join(user2_data.get('keywords', []))
                )
                total_score = (keyword_similarity * 0.8) + (doc_similarity * 0.2)
                print(f"    📊 MATCHING ANALYSIS:")
                print(f"    ├─ Strategy: Keywords + User1's document vs User2's keywords")
                print(f"    ├─ Keyword similarity: {keyword_similarity:.4f}")
                print(f"    ├─ Document similarity: {doc_similarity:.4f}")
                print(f"    ├─ Weighted: ({keyword_similarity:.4f} × 0.8) + ({doc_similarity:.4f} × 0.2)")
                print(f"    └─ Total score: {total_score:.4f}")
                
            elif not user1_has_doc and user2_has_doc:
                # User2 has document, User1 doesn't - compare keywords to document
                doc_similarity = self.calculate_document_similarity(
                    ", ".join(user1_data.get('keywords', [])),
                    user2_data.get('document_text', '')
                )
                total_score = (keyword_similarity * 0.8) + (doc_similarity * 0.2)
                print(f"    📊 MATCHING ANALYSIS:")
                print(f"    ├─ Strategy: Keywords + User2's document vs User1's keywords")
                print(f"    ├─ Keyword similarity: {keyword_similarity:.4f}")
                print(f"    ├─ Document similarity: {doc_similarity:.4f}")
                print(f"    ├─ Weighted: ({keyword_similarity:.4f} × 0.8) + ({doc_similarity:.4f} × 0.2)")
                print(f"    └─ Total score: {total_score:.4f}")
                
            else:
                # Both users have documents - comprehensive comparison
                doc_to_doc_similarity = self.calculate_document_similarity(
                    user1_data.get('document_text', ''),
                    user2_data.get('document_text', '')
                )
                
                # User1 keywords vs User2 document
                kw1_to_doc2_similarity = self.calculate_document_similarity(
                    ", ".join(user1_data.get('keywords', [])),
                    user2_data.get('document_text', '')
                )
                
                # User2 keywords vs User1 document
                kw2_to_doc1_similarity = self.calculate_document_similarity(
                    ", ".join(user2_data.get('keywords', [])),
                    user1_data.get('document_text', '')
                )
                
                # Weighted combination: 70% keywords + 15% doc-to-doc + 7.5% kw1-to-doc2 + 7.5% kw2-to-doc1
                total_score = (
                    keyword_similarity * 0.7 +
                    doc_to_doc_similarity * 0.15 +
                    kw1_to_doc2_similarity * 0.075 +
                    kw2_to_doc1_similarity * 0.075
                )
                print(f"    📊 MATCHING ANALYSIS:")
                print(f"    ├─ Strategy: Comprehensive (both users have documents)")
                print(f"    ├─ Keyword similarity: {keyword_similarity:.4f}")
                print(f"    ├─ Document-to-Document similarity: {doc_to_doc_similarity:.4f}")
                print(f"    ├─ User1 keywords vs User2 document: {kw1_to_doc2_similarity:.4f}")
                print(f"    ├─ User2 keywords vs User1 document: {kw2_to_doc1_similarity:.4f}")
                print(f"    ├─ Weighted: ({keyword_similarity:.4f} × 0.7) + ({doc_to_doc_similarity:.4f} × 0.15) + ({kw1_to_doc2_similarity:.4f} × 0.075) + ({kw2_to_doc1_similarity:.4f} × 0.075)")
                print(f"    └─ Total score: {total_score:.4f}")
            
            return total_score
            
        except Exception as e:
            logger.error(f"Error calculating match score: {e}")
            return 0.0
    
    def find_best_matches(self, current_user_data: Dict, all_users_data: List[Dict], 
                         top_k: int = 10) -> List[Tuple[Dict, float]]:
        """
        Find the best matches for a user based on semantic similarity
        
        Args:
            current_user_data: Current user's data
            all_users_data: List of all other users' data
            top_k: Number of top matches to return
            
        Returns:
            List of tuples (user_data, match_score) sorted by score
        """
        try:
            matches = []
            
            for user_data in all_users_data:
                # Skip self-matching
                if user_data.get('user_id') == current_user_data.get('user_id'):
                    continue
                
                # Calculate match score
                score = self.calculate_match_score(current_user_data, user_data)
                
                # Only include matches with optimal threshold (0.26) based on evaluation
                if score > 0.26:
                    matches.append((user_data, score))
            
            # Sort by score (highest first) and return top_k
            matches.sort(key=lambda x: x[1], reverse=True)
            return matches[:top_k]
            
        except Exception as e:
            logger.error(f"Error finding best matches: {e}")
            return []

# Global instance
matching_engine = MatchingEngine()
