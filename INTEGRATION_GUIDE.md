# DeepSeek API Integration Guide

Your DeepSeek API is now live at: **https://deepseek-api-tbp3.onrender.com**

## 🔌 Integration with InsightFlow AI Trading App

### Option 1: Add as LongCat Alternative (Recommended)

Update your `insightflow_ai_trading/lib/services/ai_service.dart`:

```dart
// Add DeepSeek as a fallback provider
Future<String> generateInsights(String prompt) async {
  try {
    // Try LongCat first
    return await _generateWithLongCat(prompt);
  } catch (e) {
    logger.warning('LongCat failed, trying DeepSeek: $e');

    try {
      // Fallback to your DeepSeek API
      return await _generateWithDeepSeek(prompt);
    } catch (e2) {
      logger.warning('DeepSeek failed, trying OpenAI: $e2');
      return await _generateWithOpenAI(prompt);
    }
  }
}

Future<String> _generateWithDeepSeek(String prompt) async {
  final response = await http.post(
    Uri.parse('https://deepseek-api-tbp3.onrender.com/v1/chat/completions'),
    headers: {
      'Content-Type': 'application/json',
    },
    body: jsonEncode({
      'model': 'deepseek-r1:1.5b',
      'messages': [
        {'role': 'user', 'content': prompt}
      ],
      'max_tokens': 2048,
      'temperature': 0.7,
    }),
  );

  if (response.statusCode == 200) {
    final data = jsonDecode(response.body);
    return data['choices'][0]['message']['content'];
  } else {
    throw Exception('DeepSeek API failed: ${response.statusCode}');
  }
}
```

### Option 2: Replace LongCat Entirely

Update your `.env` file:

```env
# Replace LongCat with your DeepSeek API
DEEPSEEK_API_URL=https://deepseek-api-tbp3.onrender.com
```

Then update your AI service to use DeepSeek as primary:

```dart
Future<String> generateInsights(String prompt) async {
  final deepseekUrl = dotenv.env['DEEPSEEK_API_URL'];

  if (deepseekUrl != null && deepseekUrl.isNotEmpty) {
    try {
      return await _generateWithDeepSeek(prompt);
    } catch (e) {
      logger.warning('DeepSeek failed, falling back to OpenAI: $e');
      return await _generateWithOpenAI(prompt);
    }
  }

  return await _generateWithOpenAI(prompt);
}
```

## 📊 API Endpoints

### 1. Chat Completions (Recommended)
```bash
POST https://deepseek-api-tbp3.onrender.com/v1/chat/completions
Content-Type: application/json

{
  "model": "deepseek-r1:1.5b",
  "messages": [
    {"role": "user", "content": "Analyze this trading pattern..."}
  ],
  "max_tokens": 2048,
  "temperature": 0.7
}
```

### 2. Text Completions
```bash
POST https://deepseek-api-tbp3.onrender.com/v1/completions
Content-Type: application/json

{
  "model": "deepseek-r1:1.5b",
  "prompt": "Based on the following trade data...",
  "max_tokens": 2048
}
```

### 3. Health Check
```bash
GET https://deepseek-api-tbp3.onrender.com/health
```

### 4. List Models
```bash
GET https://deepseek-api-tbp3.onrender.com/v1/models
```

## 🎯 Use Cases in Your App

### 1. Trading Insights
```dart
final insights = await _generateWithDeepSeek('''
Analyze the following trading data:
- Win Rate: 65%
- Average P&L: \$250
- Total Trades: 45
- Best Day: Monday

Provide actionable insights and improvement suggestions.
''');
```

### 2. AI Coach Messages
```dart
final coachResponse = await _generateWithDeepSeek('''
User asked: "Why am I losing money on Fridays?"

Portfolio data:
- Friday trades: 12 (8 losses, 4 wins)
- Average loss: \$150
- Common pattern: End-of-week fatigue

Provide coaching advice as a supportive AI trading coach.
''');
```

### 3. Journal Entry Analysis
```dart
final analysis = await _generateWithDeepSeek('''
Analyze this trading journal entry:
"${journalEntry.content}"

Mood: ${journalEntry.mood}
Date: ${journalEntry.createdAt}

Identify patterns and provide feedback.
''');
```

## ⚙️ Configuration Options

### Adjust Response Length
```dart
'max_tokens': 500,  // Shorter responses (faster, cheaper)
'max_tokens': 2048, // Longer responses (more detailed)
```

### Control Creativity
```dart
'temperature': 0.3, // More focused, deterministic
'temperature': 0.7, // Balanced (recommended)
'temperature': 1.0, // More creative, varied
```

### Enable Streaming
```dart
final response = await http.post(
  Uri.parse('https://deepseek-api-tbp3.onrender.com/v1/chat/completions'),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({
    'model': 'deepseek-r1:1.5b',
    'messages': messages,
    'stream': true, // Enable streaming
  }),
);

// Handle streaming response
response.stream
  .transform(utf8.decoder)
  .transform(const LineSplitter())
  .listen((line) {
    if (line.startsWith('data: ')) {
      final data = jsonDecode(line.substring(6));
      final content = data['choices'][0]['delta']['content'];
      // Update UI with streamed content
    }
  });
```

## 🚨 Important Notes

### Cold Start Warning
- **First request after idle:** ~30 seconds (Render spins up the service)
- **Subsequent requests:** ~2-5 seconds
- **Recommendation:** Add loading state in your UI

### Rate Limits
- **Free tier:** Unlimited requests
- **Timeout:** 120 seconds per request
- **Concurrent requests:** 25 max

### Error Handling
```dart
try {
  final result = await _generateWithDeepSeek(prompt);
  return result;
} on SocketException catch (e) {
  // Network error - API might be cold starting
  logger.warning('Network error, retrying in 5s...');
  await Future.delayed(Duration(seconds: 5));
  return await _generateWithDeepSeek(prompt); // Retry once
} on TimeoutException catch (e) {
  // Request timed out
  logger.error('DeepSeek timeout: $e');
  throw Exception('AI service is taking too long');
} catch (e) {
  // Other errors
  logger.error('DeepSeek error: $e');
  rethrow;
}
```

## 📈 Monitoring

### Check API Status
```bash
curl https://deepseek-api-tbp3.onrender.com/health
```

### View Logs
1. Go to https://dashboard.render.com
2. Select "deepseek-api" service
3. Click "Logs" tab

## 🔧 Troubleshooting

### Issue: First request times out
**Solution:** This is normal - Render spins down after 15min idle. Second request will work.

### Issue: "Model not loaded" error
**Solution:** Model loads on first request. Wait 30-60 seconds and retry.

### Issue: Slow responses
**Solution:**
- Reduce `max_tokens` to 500-1000
- Use `temperature: 0.3` for faster, more focused responses
- Consider upgrading to paid Render tier ($7/month for faster instance)

## 💰 Cost Optimization

### Current Setup (FREE)
- **Render Free Tier:** $0/month
- **Bandwidth:** 100GB/month free
- **Compute:** 750 hours/month free

### To Scale Up (Optional)
```bash
# Upgrade to Starter ($7/month) for:
# - No spin down
# - More RAM (1GB)
# - Faster responses
```

## 🎉 Ready to Use!

Your DeepSeek API is production-ready and can handle:
- ✅ Trading insights generation
- ✅ AI coaching responses
- ✅ Journal entry analysis
- ✅ Pattern recognition
- ✅ Real-time chat

Just add the integration code to your `ai_service.dart` and you're good to go!
