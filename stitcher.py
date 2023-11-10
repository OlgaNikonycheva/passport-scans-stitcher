import fitz
import os
import argparse

zoom = 3
gap = 25
mat = fitz.Matrix(zoom, zoom)


def stitch_pages(input_pdf_path, output_pdf_path):
    doc_src = fitz.Document(input_pdf_path)
    doc_dest = fitz.Document()

    counter = 0

    a4 = fitz.paper_size("A4")
    a4_width, a4_height = a4

    images_to_delete = []

    for page in doc_src:
        pix: fitz.Pixmap = page.get_pixmap(matrix=mat)

        out_img = f"./{counter}.jpg"
        pix.pil_save(out_img, format="JPEG", subsampling=0, quality=75)

        images_to_delete.append(out_img)

        if counter % 2 == 0:
            rect = fitz.Rect(gap, gap, a4_width - gap, a4_height / 2 - gap)
            out_page: fitz.Page = doc_dest.new_page(width=a4_width, height=a4_height)

        else:
            rect = fitz.Rect(gap, a4_height / 2 + gap, a4_width - gap, a4_height - gap)

        with open(out_img, "rb") as f:
            out_page.insert_image(rect, stream=f.read())

        counter += 1

    for img_path in images_to_delete:
        os.remove(img_path)

    doc_dest.save(output_pdf_path)
    doc_src.close()
    doc_dest.close()


def replace_and_stitch(input_pdf_path, output_pdf_path, replacement_pdf_path, page_num, position):
    doc_dest = fitz.open(input_pdf_path)
    doc_replacement = fitz.open(replacement_pdf_path)

    replacement_page = doc_replacement[0]
    pix: fitz.Pixmap = replacement_page.get_pixmap(matrix=mat)
    out_img = f"./1.jpg"
    pix.pil_save(out_img, format="JPEG", subsampling=0, quality=75)

    page_index = page_num - 1
    old_page = doc_dest[page_index]
    crop_rect = old_page.rect

    if position == "top":
        crop_rect.y1 = crop_rect.y0 + crop_rect.height / 2
    elif position == "bottom":
        crop_rect.y0 = crop_rect.y0 + crop_rect.height / 2

    crop_rect.x0 += gap
    crop_rect.y0 += gap
    crop_rect.x1 -= gap
    crop_rect.y1 -= gap

    with open(out_img, "rb") as img_file:
        img_data = img_file.read()
        old_page.insert_image(rect=crop_rect, stream=img_data)

    os.remove(out_img)
    doc_dest.save(output_pdf_path)
    doc_dest.close()
    doc_replacement.close()


def main():
    parser = argparse.ArgumentParser(description="PDF Stitching and Page Replacement")

    parser.add_argument("-i", "--input_pdf", help="Input PDF document")
    parser.add_argument("-o", "--output_pdf", help="Output PDF document")
    parser.add_argument("-r", "--replacement_pdf", help="Path to replacement PDF page")
    parser.add_argument(
        "-p",
        "--page_num",
        type=int,
        help="Page number in passport to be replaced"
    )
    parser.add_argument(
        "--position",
        choices=["top", "bottom"],
        help="Position to insert the new image (top/bottom)",
        default="top",
    )

    args = parser.parse_args()

    if args.replacement_pdf and args.page_num is not None and args.position:
        replace_and_stitch(args.input_pdf, args.output_pdf, args.replacement_pdf, args.page_num, args.position)
    elif args.input_pdf and args.output_pdf:
        stitch_pages(args.input_pdf, args.output_pdf)
    else:
        print("Invalid arguments. Please provide the necessary information.")


if __name__ == "__main__":
    main()
