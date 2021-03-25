python -c "import pyttsx3; print(*[voice.id for voice in pyttsx3.init().getProperty('voices')], sep='\n')"
