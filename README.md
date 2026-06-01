# 🎹 Piano Tiles

A beautiful, feature-rich music rhythm game inspired by Piano Tiles, built with Python and Pygame.

**言語**: [日本語](README.ja.md) | English

## ✨ Features

- 🎵 **4-lane rhythm game** with smooth scrolling mechanics
- 🎼 **Auto-generated charts** using audio analysis (onset detection, spectral analysis)
- 🎨 **Beautiful visual effects** with glow, shadows, and particle systems
- ⌨️ **Customizable key bindings** for comfortable play
- ⚙️ **Adjustable difficulty levels** (EASY, NORMAL, HARD, PRO)
- 📊 **Professional result screen** with accuracy rating and statistics
- 🎼 **Chart editor** for creating custom songs
- 🔊 **Sound effects** for different judge ratings
- 💾 **Persistent configuration** and high score saving

## 🚀 Quick Start

### Requirements

- Python 3.9 or higher
- pip or poetry

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/piano-tiles.git
   cd piano-tiles
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   # or using poetry
   poetry install
   ```

4. **Run the game**
   ```bash
   python main.py
   ```

## 📂 Project Structure

```
piano-tiles/
├── main.py                    # Entry point
├── constants.py               # Game constants and settings
├── classes.py                 # Game objects and effects
├── classes_professional.py    # Professional version with type hints
├── chart_generator.py         # Auto-generated chart logic
├── config.py                  # Configuration management
├── exceptions.py              # Custom exceptions
├── logger.py                  # Logging system
├── resource_manager.py        # Resource management (fonts, sounds, images)
├── ui_screens.py              # UI screens (menu, options, song select)
├── utils.py                   # Utility functions
│
├── assets/
│   ├── music/                 # Game music files
│   │   ├── arabesque1.wav
│   │   ├── moonlight.wav
│   │   └── ...
│   └── sounds/                # Sound effects
│       ├── perfect.wav
│       ├── great.wav
│       ├── good.wav
│       └── miss.wav
│
├── logs/                      # Game logs
├── config.json               # Game configuration (auto-generated)
│
├── pyproject.toml            # Project metadata
├── README.md                 # This file
└── .gitignore               # Git ignore rules
```

## 🎮 How to Play

### Controls

| Key     | Action         |
| ------- | -------------- |
| `D`     | Lane 1         |
| `F`     | Lane 2         |
| `J`     | Lane 3         |
| `K`     | Lane 4         |
| `↑↓`    | Navigate menu  |
| `SPACE` | Select/Confirm |
| `ESC`   | Back/Quit      |

### Gameplay

1. **Press keys** to match notes falling down the screen
2. **Hold keys** for long notes
3. **Timing matters**: Perfect, Great, Good, or Miss
4. **Build combos** to increase your score
5. **Reach the bottom** without missing to pass the stage

### Difficulty Levels

- **EASY**: 4分 notes only, gentle pace
- **NORMAL**: 4分 + 8分 notes mixed
- **HARD**: 4分 + 8分 + 16分 notes, challenging
- **PRO**: AI-generated from audio analysis

## 🔧 Configuration

Game settings are stored in `config.json`:

```json
{
  "screen": {
    "width": 400,
    "height": 600,
    "fps": 60,
    "title": "Piano Tiles"
  },
  "game": {
    "difficulty": "NORMAL",
    "speed_level": 3,
    "auto_save": true,
    "debug_mode": false
  },
  "audio": {
    "master_volume": 1.0,
    "bgm_volume": 0.8,
    "se_volume": 0.9,
    "enable_sound": true
  },
  "keys": {
    "lane1": "d",
    "lane2": "f",
    "lane3": "j",
    "lane4": "k"
  }
}
```

## 📚 Code Architecture

### Type Hints and Documentation

All code includes:

- ✅ Full type hints for function parameters and return values
- ✅ Comprehensive docstrings following Google style
- ✅ Clear variable naming conventions
- ✅ Modular, maintainable structure

### Professional Features

- **Error Handling**: Custom exceptions for specific error cases
- **Logging**: Structured logging with file output
- **Resource Management**: Efficient caching of fonts, sounds, images
- **Configuration**: External config file for easy customization
- **Type Safety**: Full type checking support with mypy

## 🧪 Testing

Run tests with pytest:

```bash
pytest
pytest --cov=.  # With coverage report
```

## 🎨 Code Style

The project follows PEP 8 with Black formatting:

```bash
# Format code
black .

# Check style
flake8 .

# Type check
mypy .
```

## 🎼 Adding Custom Songs

1. Place your audio file in `assets/music/`
2. Add song info to the song list in `main.py`
3. Optionally create a `{song_name}_chart.json` for custom charts

Example song entry:

```python
{
    "title": "My Song",
    "file": "assets/music/my_song.wav",
    "jacket": make_jacket((255, 120, 120)),
    "difficulty": 5,
    "bpm": 120,
    "length": 0,
    "chart": [],
    "notes": [],
}
```

## 📈 Performance Tips

- **Auto-save**: Enabled by default, can be disabled in config
- **FPS Cap**: Default 60 FPS, adjust in constants.py
- **Resource Caching**: Fonts and sounds are cached on first load
- **Debug Mode**: Disable for production use

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Credits

- **Pygame**: Game development framework
- **Librosa**: Audio analysis library
- **Music**: Classical piano pieces from public domain sources

## 📧 Contact

- **Issues**: [GitHub Issues](https://github.com/yourusername/piano-tiles/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/piano-tiles/discussions)

## 🗺️ Roadmap

- [ ] Multiplayer mode
- [ ] More visual themes
- [ ] Mobile support
- [ ] Song sharing platform
- [ ] Replay system
- [ ] Daily challenges
- [ ] Leaderboards

---

**Last Updated**: May 28, 2026
