import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import { Slider } from '@/components/ui/slider.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar.jsx'
import { 
  Search, 
  Brain, 
  Cpu, 
  Zap, 
  Users, 
  TrendingUp, 
  Filter, 
  Star, 
  Clock, 
  DollarSign, 
  Wrench, 
  ChevronRight,
  MessageCircle,
  BookOpen,
  Activity,
  Target,
  Lightbulb,
  Code,
  Settings,
  Play,
  Eye,
  Heart,
  Share2,
  Download,
  Menu,
  X,
  Camera,
  Wifi
} from 'lucide-react'
import './App.css'
import logo from './assets/logo.png'
import heroBg from './assets/hero-bg.png'
import aiBrain from './assets/ai-brain.png'
import EnhancedFeatures from './components/EnhancedFeatures'

// Sample project data
const sampleProjects = [
  {
    id: 1,
    title: "Smart Home Security System",
    description: "Build an AI-powered security system with facial recognition and mobile alerts",
    difficulty: "Intermediate",
    cost: 150,
    duration: "2-3 days",
    category: "Security",
    tags: ["AI", "IoT", "Security", "Raspberry Pi"],
    rating: 4.8,
    views: 1250,
    likes: 89,
    components: ["Raspberry Pi 4", "Camera Module", "PIR Sensor", "Buzzer"],
    skills: ["Python", "OpenCV", "Electronics"],
    image: "/api/placeholder/300/200"
  },
  {
    id: 2,
    title: "Autonomous Flying Robot",
    description: "Create a self-navigating drone with obstacle avoidance and GPS tracking",
    difficulty: "Advanced",
    cost: 300,
    duration: "1 week",
    category: "Robotics",
    tags: ["Drone", "AI", "GPS", "Sensors"],
    rating: 4.9,
    views: 2100,
    likes: 156,
    components: ["Flight Controller", "GPS Module", "Ultrasonic Sensors", "Camera"],
    skills: ["C++", "Flight Control", "Electronics"],
    image: "/api/placeholder/300/200"
  },
  {
    id: 3,
    title: "Voice-Controlled LED Matrix",
    description: "Build a smart LED display that responds to voice commands and shows animations",
    difficulty: "Beginner",
    cost: 75,
    duration: "1 day",
    category: "Display",
    tags: ["Voice Control", "LED", "Arduino", "Audio"],
    rating: 4.6,
    views: 890,
    likes: 67,
    components: ["Arduino Uno", "LED Matrix", "Microphone Module", "Speaker"],
    skills: ["Arduino", "Basic Electronics"],
    image: "/api/placeholder/300/200"
  }
]

// Learning activity data
const learningActivities = [
  { time: "2 minutes ago", activity: "Discovered new IoT sensor technology", type: "discovery" },
  { time: "5 minutes ago", activity: "Merged concepts: 'smart lighting' + 'motion detection'", type: "merge" },
  { time: "10 minutes ago", activity: "Updated component prices from 3 suppliers", type: "price" },
  { time: "15 minutes ago", activity: "Learned from user feedback on drone project", type: "feedback" },
  { time: "20 minutes ago", activity: "Generated new project: Smart Plant Watering System", type: "generation" }
]

function Header({ onMenuToggle, isMenuOpen }) {
  return (
    <header className="bg-white/95 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-4">
            <img src={logo} alt="TechCraft Genius AI" className="h-10 w-10" />
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                TechCraft Genius AI
              </h1>
              <p className="text-xs text-gray-500">Revolutionary DIY Platform</p>
            </div>
          </div>
          
          <nav className="hidden md:flex items-center space-x-8">
            <Link to="/" className="text-gray-700 hover:text-blue-600 transition-colors">Home</Link>
            <Link to="/projects" className="text-gray-700 hover:text-blue-600 transition-colors">Projects</Link>
            <Link to="/ai-chat" className="text-gray-700 hover:text-blue-600 transition-colors">AI Assistant</Link>
            <Link to="/learning" className="text-gray-700 hover:text-blue-600 transition-colors">Learning</Link>
            <Link to="/community" className="text-gray-700 hover:text-blue-600 transition-colors">Community</Link>
          </nav>

          <div className="flex items-center space-x-4">
            <Button variant="outline" size="sm" className="hidden sm:flex">
              <Users className="h-4 w-4 mr-2" />
              Join Community
            </Button>
            <Button className="md:hidden" variant="ghost" size="sm" onClick={onMenuToggle}>
              {isMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </Button>
          </div>
        </div>
      </div>
    </header>
  )
}

function HomePage() {
  const [searchQuery, setSearchQuery] = useState('')
  
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 text-white overflow-hidden">
        <div 
          className="absolute inset-0 opacity-20"
          style={{
            backgroundImage: `url(${heroBg})`,
            backgroundSize: 'cover',
            backgroundPosition: 'center'
          }}
        />
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h1 className="text-5xl lg:text-6xl font-bold mb-6 leading-tight">
                Revolutionary
                <span className="block bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
                  AI-Powered
                </span>
                DIY Platform
              </h1>
              <p className="text-xl text-gray-300 mb-8 leading-relaxed">
                Experience the future of DIY tech projects with our genius AI that learns, creates, and evolves. 
                From concept merging to real-time learning, discover unlimited possibilities.
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <Button size="lg" className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
                  <Zap className="h-5 w-5 mr-2" />
                  Explore Projects
                </Button>
                <Button size="lg" variant="outline" className="border-white text-white hover:bg-white hover:text-gray-900">
                  <Brain className="h-5 w-5 mr-2" />
                  Try AI Assistant
                </Button>
              </div>
            </div>
            <div className="relative">
              <img 
                src={aiBrain} 
                alt="AI Brain" 
                className="w-full max-w-md mx-auto animate-pulse"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              World-Class AI Capabilities
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Our revolutionary AI doesn't just store projects—it creates, learns, and evolves continuously
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow">
              <CardHeader>
                <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-lg flex items-center justify-center mb-4">
                  <Lightbulb className="h-6 w-6 text-white" />
                </div>
                <CardTitle>Concept Merging</CardTitle>
                <CardDescription>
                  AI intelligently combines ideas like "flying" + "robot" with 95% synergy scoring
                </CardDescription>
              </CardHeader>
            </Card>
            
            <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow">
              <CardHeader>
                <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center justify-center mb-4">
                  <TrendingUp className="h-6 w-6 text-white" />
                </div>
                <CardTitle>Continuous Learning</CardTitle>
                <CardDescription>
                  Real-time web discovery, price monitoring, and community feedback integration
                </CardDescription>
              </CardHeader>
            </Card>
            
            <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow">
              <CardHeader>
                <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-emerald-500 rounded-lg flex items-center justify-center mb-4">
                  <Target className="h-6 w-6 text-white" />
                </div>
                <CardTitle>Smart Optimization</CardTitle>
                <CardDescription>
                  Cost optimization, difficulty scaling, and equipment matching for perfect projects
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </div>
      </section>

      {/* Quick Search */}
      <section className="py-16 bg-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-8">
            Find Your Perfect Project
          </h2>
          <div className="relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <Input
              type="text"
              placeholder="Search for projects, ask questions, or describe what you want to build..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-12 pr-4 py-4 text-lg border-2 border-gray-200 focus:border-blue-500 rounded-xl"
            />
          </div>
          <div className="mt-6 flex flex-wrap justify-center gap-2">
            {["Smart Home", "Robotics", "IoT", "AI Projects", "Arduino", "Raspberry Pi"].map((tag) => (
              <Badge key={tag} variant="secondary" className="cursor-pointer hover:bg-blue-100">
                {tag}
              </Badge>
            ))}
          </div>
        </div>
      </section>

      {/* Featured Projects */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900">Featured Projects</h2>
            <Button variant="outline">
              View All Projects
              <ChevronRight className="h-4 w-4 ml-2" />
            </Button>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            {sampleProjects.map((project) => (
              <Card key={project.id} className="border-0 shadow-lg hover:shadow-xl transition-all hover:-translate-y-1">
                <div className="aspect-video bg-gradient-to-br from-blue-100 to-purple-100 rounded-t-lg"></div>
                <CardHeader>
                  <div className="flex justify-between items-start mb-2">
                    <Badge variant={project.difficulty === 'Beginner' ? 'secondary' : project.difficulty === 'Intermediate' ? 'default' : 'destructive'}>
                      {project.difficulty}
                    </Badge>
                    <div className="flex items-center space-x-1 text-sm text-gray-500">
                      <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                      <span>{project.rating}</span>
                    </div>
                  </div>
                  <CardTitle className="text-lg">{project.title}</CardTitle>
                  <CardDescription>{project.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex justify-between items-center text-sm text-gray-500 mb-4">
                    <div className="flex items-center">
                      <DollarSign className="h-4 w-4 mr-1" />
                      ${project.cost}
                    </div>
                    <div className="flex items-center">
                      <Clock className="h-4 w-4 mr-1" />
                      {project.duration}
                    </div>
                    <div className="flex items-center">
                      <Eye className="h-4 w-4 mr-1" />
                      {project.views}
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-1 mb-4">
                    {project.tags.slice(0, 3).map((tag) => (
                      <Badge key={tag} variant="outline" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                  <Button className="w-full">
                    <Play className="h-4 w-4 mr-2" />
                    Start Project
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}

function ProjectsPage() {
  const [filters, setFilters] = useState({
    difficulty: '',
    category: '',
    costRange: [0, 500],
    duration: ''
  })
  const [searchQuery, setSearchQuery] = useState('')
  const [showFilters, setShowFilters] = useState(false)

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Explore Projects</h1>
          <p className="text-xl text-gray-600">Discover our ever-growing collection of AI-curated DIY tech projects</p>
        </div>

        {/* Search and Filters */}
        <div className="bg-white rounded-xl shadow-sm border p-6 mb-8">
          <div className="flex flex-col lg:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <Input
                type="text"
                placeholder="Search projects, components, or ask the AI..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
            <Button 
              variant="outline" 
              onClick={() => setShowFilters(!showFilters)}
              className="lg:w-auto"
            >
              <Filter className="h-4 w-4 mr-2" />
              Filters
            </Button>
          </div>

          {showFilters && (
            <div className="mt-6 pt-6 border-t grid md:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Difficulty</label>
                <Select value={filters.difficulty} onValueChange={(value) => setFilters({...filters, difficulty: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Any difficulty" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="beginner">Beginner</SelectItem>
                    <SelectItem value="intermediate">Intermediate</SelectItem>
                    <SelectItem value="advanced">Advanced</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
                <Select value={filters.category} onValueChange={(value) => setFilters({...filters, category: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Any category" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="robotics">Robotics</SelectItem>
                    <SelectItem value="iot">IoT</SelectItem>
                    <SelectItem value="security">Security</SelectItem>
                    <SelectItem value="display">Display</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Cost Range: ${filters.costRange[0]} - ${filters.costRange[1]}
                </label>
                <Slider
                  value={filters.costRange}
                  onValueChange={(value) => setFilters({...filters, costRange: value})}
                  max={500}
                  step={25}
                  className="mt-2"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Duration</label>
                <Select value={filters.duration} onValueChange={(value) => setFilters({...filters, duration: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Any duration" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1-day">1 Day</SelectItem>
                    <SelectItem value="2-3-days">2-3 Days</SelectItem>
                    <SelectItem value="1-week">1 Week</SelectItem>
                    <SelectItem value="1-month">1+ Month</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          )}
        </div>

        {/* Projects Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {sampleProjects.map((project) => (
            <Card key={project.id} className="border-0 shadow-lg hover:shadow-xl transition-all hover:-translate-y-1">
              <div className="aspect-video bg-gradient-to-br from-blue-100 to-purple-100 rounded-t-lg"></div>
              <CardHeader>
                <div className="flex justify-between items-start mb-2">
                  <Badge variant={project.difficulty === 'Beginner' ? 'secondary' : project.difficulty === 'Intermediate' ? 'default' : 'destructive'}>
                    {project.difficulty}
                  </Badge>
                  <div className="flex items-center space-x-2">
                    <div className="flex items-center space-x-1 text-sm text-gray-500">
                      <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                      <span>{project.rating}</span>
                    </div>
                    <Button variant="ghost" size="sm">
                      <Heart className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
                <CardTitle className="text-lg">{project.title}</CardTitle>
                <CardDescription>{project.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center text-sm text-gray-500">
                    <div className="flex items-center">
                      <DollarSign className="h-4 w-4 mr-1" />
                      ${project.cost}
                    </div>
                    <div className="flex items-center">
                      <Clock className="h-4 w-4 mr-1" />
                      {project.duration}
                    </div>
                    <div className="flex items-center">
                      <Eye className="h-4 w-4 mr-1" />
                      {project.views}
                    </div>
                  </div>
                  
                  <div className="flex flex-wrap gap-1">
                    {project.tags.slice(0, 3).map((tag) => (
                      <Badge key={tag} variant="outline" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                  
                  <div className="flex gap-2">
                    <Button className="flex-1">
                      <Play className="h-4 w-4 mr-2" />
                      Start
                    </Button>
                    <Button variant="outline" size="sm">
                      <Share2 className="h-4 w-4" />
                    </Button>
                    <Button variant="outline" size="sm">
                      <Download className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  )
}

function AIChatPage() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'ai',
      content: "Hello! I'm your TechCraft Genius AI assistant. I can help you find projects, merge concepts, optimize costs, and create custom solutions. What would you like to build today?",
      timestamp: new Date()
    }
  ])
  const [inputMessage, setInputMessage] = useState('')

  const sendMessage = () => {
    if (!inputMessage.trim()) return
    
    const newMessage = {
      id: messages.length + 1,
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    }
    
    setMessages([...messages, newMessage])
    setInputMessage('')
    
    // Simulate AI response
    setTimeout(() => {
      const aiResponse = {
        id: messages.length + 2,
        type: 'ai',
        content: "I understand you're interested in that project! Let me analyze the requirements and suggest the best approach. Based on my continuous learning, I can recommend optimal components and provide step-by-step guidance.",
        timestamp: new Date()
      }
      setMessages(prev => [...prev, aiResponse])
    }, 1000)
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">AI Assistant</h1>
          <p className="text-xl text-gray-600">Chat with our genius AI for project guidance, concept merging, and creative solutions</p>
        </div>

        <Card className="border-0 shadow-lg">
          <CardHeader className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-t-lg">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                <Brain className="h-6 w-6" />
              </div>
              <div>
                <CardTitle>TechCraft Genius AI</CardTitle>
                <CardDescription className="text-blue-100">
                  Continuously learning • Concept merging • Real-time optimization
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          
          <CardContent className="p-0">
            <div className="h-96 overflow-y-auto p-6 space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                      message.type === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-900'
                    }`}
                  >
                    <p>{message.content}</p>
                    <p className={`text-xs mt-1 ${
                      message.type === 'user' ? 'text-blue-100' : 'text-gray-500'
                    }`}>
                      {message.timestamp.toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
            
            <div className="border-t p-4">
              <div className="flex space-x-2">
                <Input
                  type="text"
                  placeholder="Ask about projects, request concept merging, or describe what you want to build..."
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                  className="flex-1"
                />
                <Button onClick={sendMessage}>
                  <MessageCircle className="h-4 w-4 mr-2" />
                  Send
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <div className="mt-8 grid md:grid-cols-3 gap-4">
          <Card className="border-0 shadow-sm hover:shadow-md transition-shadow cursor-pointer">
            <CardContent className="p-4 text-center">
              <Lightbulb className="h-8 w-8 mx-auto mb-2 text-yellow-500" />
              <h3 className="font-semibold">Concept Merging</h3>
              <p className="text-sm text-gray-600">Combine two ideas into innovative projects</p>
            </CardContent>
          </Card>
          
          <Card className="border-0 shadow-sm hover:shadow-md transition-shadow cursor-pointer">
            <CardContent className="p-4 text-center">
              <DollarSign className="h-8 w-8 mx-auto mb-2 text-green-500" />
              <h3 className="font-semibold">Cost Optimization</h3>
              <p className="text-sm text-gray-600">Find the cheapest components and alternatives</p>
            </CardContent>
          </Card>
          
          <Card className="border-0 shadow-sm hover:shadow-md transition-shadow cursor-pointer">
            <CardContent className="p-4 text-center">
              <Wrench className="h-8 w-8 mx-auto mb-2 text-blue-500" />
              <h3 className="font-semibold">Equipment Matching</h3>
              <p className="text-sm text-gray-600">Projects based on your available tools</p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

function LearningPage() {
  const [learningStats, setLearningStats] = useState({
    projectsLearned: 1247,
    conceptsMerged: 89,
    pricesUpdated: 3421,
    userFeedback: 156
  })

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">AI Learning Dashboard</h1>
          <p className="text-xl text-gray-600">Watch our AI learn and evolve in real-time</p>
        </div>

        {/* Learning Stats */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <Card className="border-0 shadow-lg">
            <CardContent className="p-6 text-center">
              <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-lg flex items-center justify-center mx-auto mb-4">
                <BookOpen className="h-6 w-6 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900">{learningStats.projectsLearned.toLocaleString()}</h3>
              <p className="text-gray-600">Projects Learned</p>
              <div className="mt-2 flex items-center justify-center text-green-600 text-sm">
                <TrendingUp className="h-4 w-4 mr-1" />
                +23 today
              </div>
            </CardContent>
          </Card>
          
          <Card className="border-0 shadow-lg">
            <CardContent className="p-6 text-center">
              <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Lightbulb className="h-6 w-6 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900">{learningStats.conceptsMerged}</h3>
              <p className="text-gray-600">Concepts Merged</p>
              <div className="mt-2 flex items-center justify-center text-green-600 text-sm">
                <TrendingUp className="h-4 w-4 mr-1" />
                +5 today
              </div>
            </CardContent>
          </Card>
          
          <Card className="border-0 shadow-lg">
            <CardContent className="p-6 text-center">
              <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-emerald-500 rounded-lg flex items-center justify-center mx-auto mb-4">
                <DollarSign className="h-6 w-6 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900">{learningStats.pricesUpdated.toLocaleString()}</h3>
              <p className="text-gray-600">Prices Updated</p>
              <div className="mt-2 flex items-center justify-center text-green-600 text-sm">
                <TrendingUp className="h-4 w-4 mr-1" />
                +127 today
              </div>
            </CardContent>
          </Card>
          
          <Card className="border-0 shadow-lg">
            <CardContent className="p-6 text-center">
              <div className="w-12 h-12 bg-gradient-to-r from-orange-500 to-red-500 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Users className="h-6 w-6 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900">{learningStats.userFeedback}</h3>
              <p className="text-gray-600">User Feedback</p>
              <div className="mt-2 flex items-center justify-center text-green-600 text-sm">
                <TrendingUp className="h-4 w-4 mr-1" />
                +8 today
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Live Learning Activity */}
          <Card className="border-0 shadow-lg">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Activity className="h-5 w-5 mr-2 text-green-500" />
                Live Learning Activity
              </CardTitle>
              <CardDescription>Real-time AI learning and improvement</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {learningActivities.map((activity, index) => (
                  <div key={index} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                    <div className={`w-2 h-2 rounded-full mt-2 ${
                      activity.type === 'discovery' ? 'bg-blue-500' :
                      activity.type === 'merge' ? 'bg-purple-500' :
                      activity.type === 'price' ? 'bg-green-500' :
                      activity.type === 'feedback' ? 'bg-orange-500' :
                      'bg-cyan-500'
                    }`} />
                    <div className="flex-1">
                      <p className="text-sm text-gray-900">{activity.activity}</p>
                      <p className="text-xs text-gray-500">{activity.time}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Learning Progress */}
          <Card className="border-0 shadow-lg">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Target className="h-5 w-5 mr-2 text-blue-500" />
                Learning Progress
              </CardTitle>
              <CardDescription>AI knowledge expansion metrics</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium">Web Discovery</span>
                  <span className="text-sm text-gray-500">87%</span>
                </div>
                <Progress value={87} className="h-2" />
              </div>
              
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium">Concept Integration</span>
                  <span className="text-sm text-gray-500">92%</span>
                </div>
                <Progress value={92} className="h-2" />
              </div>
              
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium">Price Optimization</span>
                  <span className="text-sm text-gray-500">78%</span>
                </div>
                <Progress value={78} className="h-2" />
              </div>
              
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium">User Adaptation</span>
                  <span className="text-sm text-gray-500">95%</span>
                </div>
                <Progress value={95} className="h-2" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Recent Discoveries */}
        <Card className="border-0 shadow-lg mt-8">
          <CardHeader>
            <CardTitle>Recent AI Discoveries</CardTitle>
            <CardDescription>New technologies and trends learned by our AI</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-3 gap-4">
              <div className="p-4 bg-blue-50 rounded-lg">
                <h4 className="font-semibold text-blue-900 mb-2">New IoT Sensor</h4>
                <p className="text-sm text-blue-700">Discovered advanced environmental sensor with 40% better accuracy</p>
                <Badge variant="secondary" className="mt-2">Just learned</Badge>
              </div>
              
              <div className="p-4 bg-purple-50 rounded-lg">
                <h4 className="font-semibold text-purple-900 mb-2">Cost Optimization</h4>
                <p className="text-sm text-purple-700">Found 25% cheaper alternative for Arduino-compatible boards</p>
                <Badge variant="secondary" className="mt-2">Price update</Badge>
              </div>
              
              <div className="p-4 bg-green-50 rounded-lg">
                <h4 className="font-semibold text-green-900 mb-2">Concept Merge</h4>
                <p className="text-sm text-green-700">Successfully merged "plant care" + "AI vision" = Smart Garden Monitor</p>
                <Badge variant="secondary" className="mt-2">New project</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

function CommunityPage() {
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Community</h1>
          <p className="text-xl text-gray-600">Connect with fellow makers and share your creations</p>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Community Stats */}
          <div className="lg:col-span-1">
            <Card className="border-0 shadow-lg mb-6">
              <CardHeader>
                <CardTitle>Community Stats</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between">
                  <span>Active Members</span>
                  <span className="font-semibold">12,847</span>
                </div>
                <div className="flex justify-between">
                  <span>Projects Shared</span>
                  <span className="font-semibold">3,291</span>
                </div>
                <div className="flex justify-between">
                  <span>Success Stories</span>
                  <span className="font-semibold">1,156</span>
                </div>
                <div className="flex justify-between">
                  <span>AI Improvements</span>
                  <span className="font-semibold">847</span>
                </div>
              </CardContent>
            </Card>

            {/* Top Contributors */}
            <Card className="border-0 shadow-lg">
              <CardHeader>
                <CardTitle>Top Contributors</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {[
                  { name: "Alex Chen", projects: 23, avatar: "AC" },
                  { name: "Sarah Kim", projects: 19, avatar: "SK" },
                  { name: "Mike Johnson", projects: 17, avatar: "MJ" }
                ].map((user, index) => (
                  <div key={index} className="flex items-center space-x-3">
                    <Avatar>
                      <AvatarFallback>{user.avatar}</AvatarFallback>
                    </Avatar>
                    <div className="flex-1">
                      <p className="font-medium">{user.name}</p>
                      <p className="text-sm text-gray-500">{user.projects} projects</p>
                    </div>
                    <Badge variant="outline">{index + 1}</Badge>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Community Feed */}
          <div className="lg:col-span-2">
            <Card className="border-0 shadow-lg">
              <CardHeader>
                <CardTitle>Community Feed</CardTitle>
                <CardDescription>Latest updates from our maker community</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {[
                  {
                    user: "Alex Chen",
                    avatar: "AC",
                    time: "2 hours ago",
                    content: "Just completed the Smart Home Security System! The AI's component suggestions saved me $50. Here's my build process...",
                    likes: 24,
                    comments: 8
                  },
                  {
                    user: "Sarah Kim",
                    avatar: "SK",
                    time: "4 hours ago",
                    content: "The AI suggested merging 'plant monitoring' with 'weather prediction' - resulted in an amazing automated greenhouse system!",
                    likes: 31,
                    comments: 12
                  },
                  {
                    user: "Mike Johnson",
                    avatar: "MJ",
                    time: "6 hours ago",
                    content: "Thanks to the cost optimization feature, I built the flying robot for under $200. The AI found cheaper alternatives for every component!",
                    likes: 45,
                    comments: 15
                  }
                ].map((post, index) => (
                  <div key={index} className="border-b border-gray-100 pb-6 last:border-b-0">
                    <div className="flex items-start space-x-3">
                      <Avatar>
                        <AvatarFallback>{post.avatar}</AvatarFallback>
                      </Avatar>
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="font-medium">{post.user}</span>
                          <span className="text-sm text-gray-500">{post.time}</span>
                        </div>
                        <p className="text-gray-900 mb-3">{post.content}</p>
                        <div className="flex items-center space-x-4 text-sm text-gray-500">
                          <button className="flex items-center space-x-1 hover:text-red-500">
                            <Heart className="h-4 w-4" />
                            <span>{post.likes}</span>
                          </button>
                          <button className="flex items-center space-x-1 hover:text-blue-500">
                            <MessageCircle className="h-4 w-4" />
                            <span>{post.comments}</span>
                          </button>
                          <button className="flex items-center space-x-1 hover:text-green-500">
                            <Share2 className="h-4 w-4" />
                            <span>Share</span>
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}

function MobileMenu({ isOpen, onClose }) {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 md:hidden">
      <div className="fixed inset-0 bg-black/50" onClick={onClose} />
      <div className="fixed top-0 right-0 h-full w-64 bg-white shadow-xl">
        <div className="p-4 border-b">
          <div className="flex items-center justify-between">
            <h2 className="font-semibold">Menu</h2>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="h-5 w-5" />
            </Button>
          </div>
        </div>
        <nav className="p-4 space-y-4">
          <Link to="/" className="block text-gray-700 hover:text-blue-600 transition-colors" onClick={onClose}>
            Home
          </Link>
          <Link to="/projects" className="block text-gray-700 hover:text-blue-600 transition-colors" onClick={onClose}>
            Projects
          </Link>
          <Link to="/ai-chat" className="block text-gray-700 hover:text-blue-600 transition-colors" onClick={onClose}>
            AI Assistant
          </Link>
          <Link to="/learning" className="block text-gray-700 hover:text-blue-600 transition-colors" onClick={onClose}>
            Learning
          </Link>
          <Link to="/community" className="block text-gray-700 hover:text-blue-600 transition-colors" onClick={onClose}>
            Community
          </Link>
          <Button className="w-full mt-4">
            <Users className="h-4 w-4 mr-2" />
            Join Community
          </Button>
        </nav>
      </div>
    </div>
  )
}

function App() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  return (
    <Router>
      <div className="min-h-screen bg-white">
        <Header 
          onMenuToggle={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          isMenuOpen={isMobileMenuOpen}
        />
        <MobileMenu 
          isOpen={isMobileMenuOpen} 
          onClose={() => setIsMobileMenuOpen(false)} 
        />
        
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/projects" element={<ProjectsPage />} />
          <Route path="/ai-chat" element={<AIChatPage />} />
          <Route path="/learning" element={<LearningPage />} />
          <Route path="/community" element={<CommunityPage />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App

