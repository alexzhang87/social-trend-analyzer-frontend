import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { message, expertId, sessionId, context } = body

    // Validate required fields
    if (!message || !expertId || !sessionId) {
      return NextResponse.json(
        { error: 'Missing required fields: message, expertId, sessionId' },
        { status: 400 }
      )
    }

    // Forward request to backend
    const response = await fetch(`${BACKEND_URL}/api/v1/chat/message`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({
        message,
        expert_id: expertId,
        session_id: sessionId,
        context: context || [],
        timestamp: new Date().toISOString()
      })
    })

    if (!response.ok) {
      const errorData = await response.text()
      console.error('Backend error:', errorData)
      
      return NextResponse.json(
        { 
          error: 'Failed to get response from AI service',
          details: response.status === 500 ? 'Internal server error' : 'Service unavailable'
        },
        { status: response.status }
      )
    }

    const data = await response.json()
    
    return NextResponse.json({
      response: data.response || data.message,
      metadata: {
        expertId: data.expert_id || expertId,
        sessionId: data.session_id || sessionId,
        timestamp: data.timestamp || new Date().toISOString(),
        processingTime: data.processing_time,
        model: data.model,
        tokens: data.tokens
      }
    })

  } catch (error) {
    console.error('Chat API error:', error)
    
    // Return a fallback response
    return NextResponse.json({
      response: "I apologize, but I'm experiencing technical difficulties right now. Please try again in a moment.",
      metadata: {
        error: true,
        timestamp: new Date().toISOString()
      }
    }, { status: 200 }) // Return 200 to avoid frontend error handling
  }
}

export async function GET() {
  return NextResponse.json({
    status: 'Chat API is running',
    timestamp: new Date().toISOString(),
    version: '3.0.0'
  })
}