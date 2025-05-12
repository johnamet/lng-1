"use client"

import type React from "react"

import { motion } from "framer-motion"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

interface StepFourProps {
  formData: {
    phone_number: string
  }
  updateFormData: (data: any) => void
  errors: any
}

export default function StepFour({ formData, updateFormData, errors }: StepFourProps) {
  const handlePhoneNumberChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    let value = e.target.value
    // Remove non-digit characters except +
    value = value.replace(/[^+\d]/g, "")
    // Ensure it starts with +233
    if (!value.startsWith("+233")) {
      value = "+233" + value.replace(/^\+233/, "")
    }
    // Limit to +233 and 9 digits
    if (value.length > 13) {
      value = value.slice(0, 13)
    }
    updateFormData({ phone_number: value })
  }

  return (
    <motion.div
      className="space-y-4"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
    >
      <div className="space-y-2">
        <Label htmlFor="phone_number" className={errors.phone_number ? "text-red-500" : ""}>
          Phone Number (WhatsApp)
        </Label>
        <Input
          id="phone_number"
          name="phone_number"
          value={formData.phone_number}
          onChange={handlePhoneNumberChange}
          placeholder="+233123456789"
          className={errors.phone_number ? "border-red-500 focus-visible:ring-red-500" : ""}
        />
        <p className="text-sm text-muted-foreground mt-1">
          Enter a valid Ghanaian phone number starting with +233 for WhatsApp notifications.
        </p>
        {errors.phone_number && <p className="text-sm text-red-500">{errors.phone_number}</p>}
      </div>
    </motion.div>
  )
}
