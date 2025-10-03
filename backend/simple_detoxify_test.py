"""
Simple test script to verify toxicity detection works
"""

# Test detoxify installation and basic functionality
def test_detoxify():
    try:
        from detoxify import Detoxify
        print("✅ Detoxify imported successfully")
        
        # Initialize model
        print("Loading Detoxify model...")
        model = Detoxify('original')
        print("✅ Model loaded successfully")
        
        # Test with sample texts
        test_texts = [
            "This is a great amendment that will help everyone.",
            "I disagree with this proposal but respect the process.",
            "This is absolutely stupid and you are all idiots."
        ]
        
        print("\nTesting toxicity detection:")
        print("="*50)
        
        for i, text in enumerate(test_texts, 1):
            print(f"\nTest {i}: {text}")
            
            try:
                result = model.predict(text)
                max_score = max(result.values())
                is_toxic = max_score > 0.6
                
                print(f"Max toxicity score: {max_score:.4f}")
                print(f"Is toxic (>0.6): {is_toxic}")
                
                if is_toxic:
                    print("🚫 TOXIC - Would be blocked")
                else:
                    print("✅ SAFE - Would be processed")
                    
            except Exception as e:
                print(f"❌ Error processing text: {e}")
        
        print("\n✅ Detoxify test completed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import detoxify: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_detoxify()