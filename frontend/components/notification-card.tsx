"use client"

import { motion } from "framer-motion"
import { X, CheckCircle, AlertCircle, MessageCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter } from "@/components/ui/card"

interface NotificationCardProps {
  type: "success" | "error"
  message: string
  whatsappAction?: boolean
  onWhatsAppClick?: () => void
  onClose: () => void
}

export default function NotificationCard({
  type,
  message,
  whatsappAction,
  onWhatsAppClick,
  onClose,
}: NotificationCardProps) {
  return (
    <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.3 }}>
      <Card className={`shadow-lg border-0 ${type === "success" ? "bg-green-50" : "bg-red-50"}`}>
        <CardContent className="pt-6">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              {type === "success" ? (
                <CheckCircle className="h-6 w-6 text-green-500" />
              ) : (
                <AlertCircle className="h-6 w-6 text-red-500" />
              )}
            </div>
            <div className="ml-3 flex-1">
              <h3 className={`text-lg font-medium ${type === "success" ? "text-green-800" : "text-red-800"}`}>
                {type === "success" ? "Success!" : "Error"}
              </h3>
              <div className={`mt-2 text-sm ${type === "success" ? "text-green-700" : "text-red-700"}`}>
                <p>{message}</p>
              </div>
            </div>
            <button
              type="button"
              className="ml-auto flex-shrink-0 rounded-md bg-transparent p-1 hover:bg-gray-200"
              onClick={onClose}
            >
              <X className="h-5 w-5 text-gray-500" />
            </button>
          </div>
        </CardContent>

        {whatsappAction && (
          <CardFooter className="border-t border-green-100 bg-green-50">
            <Button
              variant="outline"
              className="w-full flex items-center justify-center gap-2 text-green-700 border-green-300 hover:bg-green-100"
              onClick={onWhatsAppClick}
            >
              <MessageCircle className="h-4 w-4" />
              Open WhatsApp
            </Button>
          </CardFooter>
        )}
      </Card>
    </motion.div>
  )
}
