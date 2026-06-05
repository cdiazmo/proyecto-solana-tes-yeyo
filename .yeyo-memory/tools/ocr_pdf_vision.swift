import AppKit
import Foundation
import PDFKit
import Vision

struct OCRResult: Codable {
    let input: String
    let output: String
    let pages: Int
    let pagesWithText: Int
    let characters: Int
    let generatedAt: String
}

enum OCRError: Error, CustomStringConvertible {
    case usage
    case cannotOpenPDF(String)
    case cannotRenderPage(Int)

    var description: String {
        switch self {
        case .usage:
            return "Usage: ocr_pdf_vision <input.pdf> <output.txt> [metadata.json]"
        case .cannotOpenPDF(let path):
            return "Cannot open PDF: \(path)"
        case .cannotRenderPage(let page):
            return "Cannot render page \(page)"
        }
    }
}

func renderPage(_ page: PDFPage, scale: CGFloat) -> CGImage? {
    let bounds = page.bounds(for: .mediaBox)
    let width = max(1, Int(bounds.width * scale))
    let height = max(1, Int(bounds.height * scale))
    let colorSpace = CGColorSpaceCreateDeviceRGB()

    guard let context = CGContext(
        data: nil,
        width: width,
        height: height,
        bitsPerComponent: 8,
        bytesPerRow: 0,
        space: colorSpace,
        bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue
    ) else {
        return nil
    }

    context.setFillColor(NSColor.white.cgColor)
    context.fill(CGRect(x: 0, y: 0, width: CGFloat(width), height: CGFloat(height)))
    context.saveGState()
    context.scaleBy(x: scale, y: scale)
    page.draw(with: .mediaBox, to: context)
    context.restoreGState()

    return context.makeImage()
}

func recognizeText(in image: CGImage) throws -> String {
    let bitmap = NSBitmapImageRep(cgImage: image)
    guard let imageData = bitmap.representation(using: .png, properties: [:]) else {
        throw OCRError.cannotRenderPage(0)
    }

    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .fast
    request.usesLanguageCorrection = false

    let handler = VNImageRequestHandler(data: imageData, options: [:])
    try handler.perform([request])

    let observations = request.results ?? []
    let lines = observations.compactMap { observation in
        observation.topCandidates(1).first?.string.trimmingCharacters(in: .whitespacesAndNewlines)
    }.filter { !$0.isEmpty }

    return lines.joined(separator: "\n")
}

func writeMetadata(_ result: OCRResult, to path: String) throws {
    let encoder = JSONEncoder()
    encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
    let data = try encoder.encode(result)
    try data.write(to: URL(fileURLWithPath: path))
}

func main() throws {
    let args = CommandLine.arguments
    guard args.count == 3 || args.count == 4 else {
        throw OCRError.usage
    }

    let inputPath = args[1]
    let outputPath = args[2]
    let metadataPath = args.count == 4 ? args[3] : nil

    guard let document = PDFDocument(url: URL(fileURLWithPath: inputPath)) else {
        throw OCRError.cannotOpenPDF(inputPath)
    }

    var output: [String] = []
    var pagesWithText = 0
    let pageCount = document.pageCount

    for index in 0..<pageCount {
        try autoreleasepool {
            guard let page = document.page(at: index) else {
                throw OCRError.cannotRenderPage(index + 1)
            }

            let bounds = page.bounds(for: .mediaBox)
            let maxDimension: CGFloat = 1600
            let longestSide = max(bounds.width, bounds.height)
            let scale = min(2.0, max(0.5, maxDimension / max(1, longestSide)))
            guard let image = renderPage(page, scale: scale) else {
                throw OCRError.cannotRenderPage(index + 1)
            }

            let text = try recognizeText(in: image)
            if !text.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                pagesWithText += 1
            }
            output.append("[page \(index + 1)]\n\(text)")
        }
    }

    let finalText = output.joined(separator: "\n\n").trimmingCharacters(in: .whitespacesAndNewlines) + "\n"
    try finalText.write(toFile: outputPath, atomically: true, encoding: .utf8)

    if let metadataPath {
        let result = OCRResult(
            input: inputPath,
            output: outputPath,
            pages: pageCount,
            pagesWithText: pagesWithText,
            characters: finalText.count,
            generatedAt: ISO8601DateFormatter().string(from: Date())
        )
        try writeMetadata(result, to: metadataPath)
    }
}

do {
    try main()
} catch {
    let nsError = error as NSError
    fputs("\(error)\n", stderr)
    fputs("domain=\(nsError.domain) code=\(nsError.code) description=\(nsError.localizedDescription)\n", stderr)
    exit(1)
}
