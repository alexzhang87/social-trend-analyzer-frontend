import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { messageId, type, sessionId, expertId } = body

    // Validate required fields
    if (!messageId || !type || !sessionId) {
      return NextResponse.json(
        { error: 'Missing required fields: messageId, type, sessionId' },
        { status: 400 }
      )
    }

    // Validate feedback type
    if (!['like', 'dislike'].includes(type)) {
      return NextResponse.json(
        { error: 'Invalid feedback type. Must be "like" or "dislike"' },
        { status: 400 }
      )
    }

    // Forward request to backend
    const response = await fetch(`${BACKEND_URL}/api/v1/feedback`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({
        message_id: messageId,
        feedback_type: type,
        session_id: sessionId,
        expert_id: expertId,
        timestamp: new Date().toISOString()
      })
    })

    if (!response.ok) {
      const errorData = await response.text()
      console.error('Backend feedback error:', errorData)
      
      return NextResponse.json(
        { 
          error: 'Failed to submit feedback',
          details: response.status === 500 ? 'Internal server error' : 'Service unavailable'
        },
        { status: response.status }
      )
    }

    const data = await response.json()
    
    return NextResponse.json({
      success: true,
      message: 'Feedback submitted successfully',
      data
    })

  } catch (error) {
    console.error('Feedback API error:', error)
    
    return NextResponse.json(
      { 
        error: 'Internal server error',
        message: 'Failed to process feedback'
      },
      { status: 500 }
    )
  }
}

export async function GET() {
  return NextResponse.json({
    status: 'Feedback API is running',
    timestamp: new Date().toISOString(),
    version: '3.0.0'
  })
}